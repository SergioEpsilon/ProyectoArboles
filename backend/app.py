from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone

from models.node import Node
from models.avl import AVL
from models.bst import BST
from services.tree_service import TreeLoadService
from services.version_service import VersionService
from services.history_service import HistoryService
from services.tree_serializer import TreeSerializer
from services.flight_factory import FlightFactory

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# ── In-memory state ───────────────────────────────────────────────────────────
avl_tree = AVL()
bst_tree = BST()

# Services (each with a single responsibility).
history_service = HistoryService(max_size=50)
version_service = VersionService()


# ── Convenience aliases ───────────────────────────────────────────────────────
def _snap():
    """Capture a full snapshot of both trees."""
    return TreeSerializer.snapshot_state(avl_tree, bst_tree)


def _restore(state):
    """Restore both trees from a snapshot."""
    global avl_tree, bst_tree
    avl_tree, bst_tree = TreeSerializer.restore_state(state)


def _rebalance():
    """Rebuild the AVL tree to guarantee balance after bulk changes."""
    global avl_tree
    avl_tree = TreeSerializer.rebalance_avl(avl_tree)


def _to_dict(tree):
    """Serialize a tree root to a frontend-ready dict."""
    return TreeSerializer.to_dict(tree.root, tree)


# ── Static route ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return app.send_static_file("index.html")


# ── Tree endpoints ─────────────────────────────────────────────────────────────
@app.route("/insert", methods=["POST"])
def insert():
    """Insert a flight node with full metadata into the selected tree.

    Required: valor (ordering key), modo (AVL|BST).
    Optional flight fields are delegated to FlightFactory.
    """
    data = request.get_json(silent=True) or {}
    valor = data.get("valor")
    modo = data.get("modo")

    if valor is None:
        return (
            jsonify({"error": "El campo 'valor' es requerido y no puede ser null"}),
            400,
        )
    if modo not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    metadata = FlightFactory.build(data, valor)

    if modo == "AVL":
        history_service.push("insert-avl", _snap())
        avl_tree.insert(Node(valor, metadata))
        return jsonify({"arbol": _to_dict(avl_tree)})
    else:
        history_service.push("insert-bst", _snap())
        bst_tree.insert(Node(valor, metadata))
        return jsonify({"arbol": _to_dict(bst_tree)})


@app.route("/clear", methods=["POST"])
def clear():
    global avl_tree, bst_tree
    history_service.push("clear-all", _snap())
    avl_tree = AVL()
    bst_tree = BST()
    return jsonify({"arbol": None})


@app.route("/delete", methods=["POST"])
def delete():
    data = request.get_json(silent=True) or {}
    valor = data.get("valor")
    modo = data.get("modo")

    if valor is None:
        return (
            jsonify({"error": "El campo 'valor' es requerido y no puede ser null"}),
            400,
        )
    if modo not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    if modo == "AVL":
        history_service.push("delete-avl", _snap())
        avl_tree.delete(valor)
        _rebalance()
        return jsonify({"arbol": _to_dict(avl_tree)})
    else:
        history_service.push("delete-bst", _snap())
        bst_tree.delete(valor)
        return jsonify({"arbol": _to_dict(bst_tree)})


@app.route("/modify", methods=["POST"])
def modify_node():
    """Modify one node value (delete old + insert new) with undo support."""
    data = request.get_json(silent=True) or {}
    old_value = data.get("old_valor")
    new_value = data.get("new_valor")
    modo = data.get("modo")

    if old_value is None or new_value is None:
        return (
            jsonify({"error": "Fields 'old_valor' and 'new_valor' are required."}),
            400,
        )
    if modo not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    tree = avl_tree if modo == "AVL" else bst_tree
    try:
        target = tree.search(old_value)
    except Exception:
        target = None
    if target is None:
        return (
            jsonify({"error": f"El valor {old_value} no existe en el árbol {modo}."}),
            404,
        )

    history_service.push(f"modify-{modo.lower()}", _snap())

    # Preserve existing metadata and apply only the fields sent in this request.
    existing_metadata = target.getMetadata() if hasattr(target, "getMetadata") else {}
    aligned_metadata = TreeSerializer.update_metadata_value(
        existing_metadata, old_value, new_value
    )
    new_metadata = FlightFactory.merge(aligned_metadata, data)

    tree.delete(old_value)
    tree.insert(Node(new_value, new_metadata))

    if modo == "AVL":
        _rebalance()
    return jsonify({"arbol": _to_dict(avl_tree if modo == "AVL" else bst_tree)})


@app.route("/cancel", methods=["POST"])
def cancel_flight_subtree():
    """Cancel a flight by removing target node and all descendants."""
    data = request.get_json(silent=True) or {}
    valor = data.get("valor")
    modo = data.get("modo")

    if valor is None:
        return (
            jsonify({"error": "El campo 'valor' es requerido y no puede ser null"}),
            400,
        )
    if modo not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    tree = avl_tree if modo == "AVL" else bst_tree
    try:
        target = tree.search(valor)
    except Exception:
        target = None
    if target is None:
        return (
            jsonify({"error": f"El valor {valor} no existe en el árbol {modo}."}),
            404,
        )

    history_service.push(f"cancel-{modo.lower()}", _snap())
    parent = target.getParent()
    if parent is None:
        tree.root = None
    else:
        if parent.getLeftChild() == target:
            parent.setLeftChild(None)
        else:
            parent.setRightChild(None)
        target.setParent(None)

    if modo == "AVL":
        _rebalance()
    return jsonify({"arbol": _to_dict(avl_tree if modo == "AVL" else bst_tree)})


@app.route("/undo", methods=["POST"])
def undo_action():
    """Restore the latest snapshot to emulate Ctrl+Z behavior."""
    if history_service.is_empty():
        return jsonify({"error": "No hay acciones para deshacer."}), 409

    data = request.get_json(silent=True) or {}
    modo = data.get("modo", "AVL")
    record = history_service.pop()
    _restore(record["state"])
    return jsonify(
        {
            "arbol": _to_dict(bst_tree if modo == "BST" else avl_tree),
            "undone_action": record["action"],
        }
    )


@app.route("/traversal", methods=["POST"])
def traversal():
    data = request.get_json(silent=True) or {}
    modo = data.get("modo")
    tipo = data.get("tipo")

    tree = avl_tree if modo == "AVL" else bst_tree
    traversal_map = {
        "inorder": tree.inOrderTraversal,
        "preorder": tree.preOrderTraversal,
        "postorder": tree.posOrderTraversal,
        "level": tree.breadthFirstSearch,
    }
    if tipo not in traversal_map:
        return jsonify({"error": "Tipo de recorrido inválido"}), 400

    resultado = traversal_map[tipo]() or []
    valores = resultado if tipo == "level" else [n.getValue() for n in resultado]
    return jsonify({"resultado": valores})


@app.route("/load-json", methods=["POST"])
def load_json():
    """Load trees from user-selected JSON and return AVL/BST comparison data."""
    global avl_tree, bst_tree

    data = request.get_json(silent=True) or {}
    json_data = data.get("json_data")

    if json_data is None:
        return jsonify({"error": "The field 'json_data' is required."}), 400

    try:
        history_service.push("load-json", _snap())
        result = TreeLoadService.load_both_trees(
            json_data=json_data,
            load_mode=data.get("load_mode"),
            key_field=data.get("key_field"),
        )
        avl_tree = result["avl"]
        bst_tree = result["bst"]

        avl_dict = _to_dict(avl_tree)
        bst_dict = _to_dict(bst_tree)

        return jsonify(
            {
                "arbol": avl_dict,
                "main_avl": avl_dict,
                "comparison": {"avl": avl_dict, "bst": bst_dict},
                "properties": result["properties"],
                "load_mode": result["load_mode"],
                "detected_key": result["detected_key"],
            }
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:
        return jsonify({"error": f"Unexpected load error: {exc}"}), 500


@app.route("/export-json", methods=["POST"])
def export_tree_json():
    """Export full tree state using real hierarchical structure (not flat lists)."""
    data = request.get_json(silent=True) or {}
    active_mode = data.get("modo", "AVL")

    if active_mode not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    return jsonify(
        {
            "export_version": "1.0",
            "generated_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "active_mode": active_mode,
            "trees": {
                "AVL": {
                    "summary": TreeSerializer.compute_tree_summary(avl_tree),
                    "root": TreeSerializer.serialize_node_for_export(
                        avl_tree.root, avl_tree
                    ),
                },
                "BST": {
                    "summary": TreeSerializer.compute_tree_summary(bst_tree),
                    "root": TreeSerializer.serialize_node_for_export(
                        bst_tree.root, bst_tree
                    ),
                },
            },
            "notes": {
                "structure": "Hierarchical tree serialized with left/right child links.",
                "restriction": "Export uses real tree structure, not a flat flight list.",
            },
        }
    )


# ── Version endpoints (Point 2: Named Version System) ─────────────────────────
@app.route("/version/save", methods=["POST"])
def save_version():
    """Save current tree state under a user-defined version name."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "El campo 'name' es requerido."}), 400

    version_service.save(name, _snap())
    return jsonify(
        {
            "ok": True,
            "name": name,
            "versions": [v["name"] for v in version_service.list_versions()],
        }
    )


@app.route("/version/list", methods=["GET"])
def list_versions():
    """Return all saved versions with their timestamps."""
    return jsonify({"versions": version_service.list_versions()})


@app.route("/version/restore", methods=["POST"])
def restore_version():
    """Restore a previously saved named version."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()

    if not name or not version_service.exists(name):
        return jsonify({"error": f"La versión '{name}' no existe."}), 404

    history_service.push("restore-version", _snap())
    _restore(version_service.restore(name))

    modo = data.get("modo", "AVL")
    return jsonify(
        {"arbol": _to_dict(bst_tree if modo == "BST" else avl_tree), "name": name}
    )


if __name__ == "__main__":
    app.run(debug=True)
