from flask import Flask, request, jsonify
from flask_cors import CORS
from copy import deepcopy
from datetime import datetime, timezone

from models.node import Node
from models.avl import AVL
from models.bst import BST
from services.tree_service import TreeLoadService

app = Flask(__name__)
CORS(app)  # permite que el HTML se comunique con Flask

# Estado del árbol en memoria
avl_tree = AVL()
bst_tree = BST()

# In-memory undo history (LIFO) with a bounded size.
MAX_HISTORY = 50
history_stack = []


# Función que convierte un árbol a diccionario para enviarlo al frontend
def tree_to_dict(node, tree):
    if node is None:
        return None

    # Read optional metadata preserved from the source JSON.
    metadata = node.getMetadata() if hasattr(node, "getMetadata") else {}

    return {
        "val": node.getValue(),
        "left": tree_to_dict(node.getLeftChild(), tree),
        "right": tree_to_dict(node.getRightChild(), tree),
        "height": tree.getHeightNode(node),
        "data": metadata,
    }


def snapshot_node(node):
    """Serialize a node subtree for undo restoration."""
    if node is None:
        return None

    metadata = node.getMetadata() if hasattr(node, "getMetadata") else {}
    return {
        "val": node.getValue(),
        "data": deepcopy(metadata),
        "left": snapshot_node(node.getLeftChild()),
        "right": snapshot_node(node.getRightChild()),
    }


def snapshot_state():
    """Create a full snapshot for AVL and BST trees."""
    return {
        "avl": snapshot_node(avl_tree.root),
        "bst": snapshot_node(bst_tree.root),
    }


def build_node_from_snapshot(node_payload, parent=None):
    """Rebuild linked Node objects from a serialized snapshot."""
    if node_payload is None:
        return None

    node = Node(node_payload.get("val"), deepcopy(node_payload.get("data") or {}))
    node.setParent(parent)

    left_child = build_node_from_snapshot(node_payload.get("left"), node)
    right_child = build_node_from_snapshot(node_payload.get("right"), node)
    node.setLeftChild(left_child)
    node.setRightChild(right_child)
    return node


def restore_state(state):
    """Restore AVL and BST trees from a previously captured snapshot."""
    global avl_tree, bst_tree
    avl_tree = AVL()
    bst_tree = BST()
    avl_tree.root = build_node_from_snapshot(state.get("avl"))
    bst_tree.root = build_node_from_snapshot(state.get("bst"))


def push_history(action_name):
    """Save state before mutations so undo can roll back safely."""
    history_stack.append({
        "action": action_name,
        "state": snapshot_state(),
    })
    if len(history_stack) > MAX_HISTORY:
        history_stack.pop(0)


def collect_values_with_metadata(node, result=None):
    """Collect node values and metadata in pre-order for full AVL rebuild."""
    if result is None:
        result = []

    if node is None:
        return result

    metadata = node.getMetadata() if hasattr(node, "getMetadata") else {}
    result.append({"value": node.getValue(), "metadata": deepcopy(metadata)})
    collect_values_with_metadata(node.getLeftChild(), result)
    collect_values_with_metadata(node.getRightChild(), result)
    return result


def rebalance_avl_tree():
    """Rebuild AVL from current values to guarantee balanced shape after bulk changes."""
    global avl_tree
    values = collect_values_with_metadata(avl_tree.root)
    rebuilt = AVL()

    for item in values:
        rebuilt.insert(Node(item["value"], item["metadata"]))

    avl_tree = rebuilt


def update_metadata_value(metadata, old_value, new_value):
    """Keep metadata key fields aligned when a node value is modified."""
    if not isinstance(metadata, dict):
        return {}

    updated = deepcopy(metadata)
    for key in ("valor", "value", "codigo", "id", "key"):
        if key in updated and updated[key] == old_value:
            updated[key] = new_value
    return updated


def get_metadata_value(metadata, keys, default=None):
    """Read the first available metadata field from multiple aliases."""
    if not isinstance(metadata, dict):
        return default

    for key in keys:
        if key in metadata:
            return metadata[key]
    return default


def compute_balance_factor(tree, node):
    """Compute AVL-like balance factor for any tree node (left height - right height)."""
    left_height = tree.getHeightNode(node.getLeftChild()) if node.getLeftChild() is not None else -1
    right_height = tree.getHeightNode(node.getRightChild()) if node.getRightChild() is not None else -1
    return left_height - right_height


def serialize_node_for_export(node, tree):
    """Serialize full hierarchical node payload for JSON export."""
    if node is None:
        return None

    metadata = node.getMetadata() if hasattr(node, "getMetadata") else {}

    # Use flexible aliases to preserve business fields from mixed JSON schemas.
    base_price = get_metadata_value(metadata, ("precio_base", "base_price", "precioBase"))
    final_price = get_metadata_value(metadata, ("precio_final", "final_price", "precioFinal"))
    passengers = get_metadata_value(metadata, ("pasajeros", "passengers"), 0)
    promotions = get_metadata_value(metadata, ("promociones", "promotions"), [])
    alerts = get_metadata_value(metadata, ("alertas", "alerts"), [])
    priority = get_metadata_value(metadata, ("prioridad", "priority"), "normal")

    if promotions is None:
        promotions = []
    if alerts is None:
        alerts = []

    return {
        "value": node.getValue(),
        "height": tree.getHeightNode(node),
        "balance_factor": compute_balance_factor(tree, node),
        "base_price": base_price,
        "final_price": final_price,
        "passengers": passengers,
        "promotions": promotions,
        "alerts": alerts,
        "priority": priority,
        "metadata": deepcopy(metadata),
        "left": serialize_node_for_export(node.getLeftChild(), tree),
        "right": serialize_node_for_export(node.getRightChild(), tree),
    }


def compute_tree_summary_for_export(tree):
    """Build summary metrics for exported trees."""
    properties = TreeLoadService.compute_tree_properties(tree)
    return {
        "root": properties["root"],
        "depth": properties["depth"],
        "nodes": properties["nodes"],
        "leaves": properties["leaves"],
    }


# Endpoint para insertar un nodo
@app.route("/insert", methods=["POST"])
def insert():
    data = request.get_json(silent=True) or {}
    valor = data.get("valor")
    modo = data.get("modo")  # 'AVL' o 'BST'

    if valor is None:
        return jsonify({"error": "El campo 'valor' es requerido y no puede ser null"}), 400

    if modo not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    node = Node(valor)

    if modo == "AVL":
        push_history("insert-avl")
        avl_tree.insert(node)
        arbol = tree_to_dict(avl_tree.root, avl_tree)
    else:
        push_history("insert-bst")
        bst_tree.insert(node)
        arbol = tree_to_dict(bst_tree.root, bst_tree)

    return jsonify({"arbol": arbol})


# Endpoint para limpiar el árbol
@app.route("/clear", methods=["POST"])
def clear():
    global avl_tree, bst_tree
    push_history("clear-all")
    avl_tree = AVL()
    bst_tree = BST()
    return jsonify({"arbol": None})


# Endpoint para eliminar un nodo
@app.route("/delete", methods=["POST"])
def delete():
    data = request.get_json(silent=True) or {}
    valor = data.get("valor")
    modo = data.get("modo")

    if valor is None:
        return jsonify({"error": "El campo 'valor' es requerido y no puede ser null"}), 400

    if modo not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    if modo == "AVL":
        push_history("delete-avl")
        avl_tree.delete(valor)
        rebalance_avl_tree()
        arbol = tree_to_dict(avl_tree.root, avl_tree)
    else:
        push_history("delete-bst")
        bst_tree.delete(valor)
        arbol = tree_to_dict(bst_tree.root, bst_tree)

    return jsonify({"arbol": arbol})


@app.route("/modify", methods=["POST"])
def modify_node():
    """Modify one node value (delete old + insert new) with undo support."""
    data = request.get_json(silent=True) or {}
    old_value = data.get("old_valor")
    new_value = data.get("new_valor")
    modo = data.get("modo")

    if old_value is None or new_value is None:
        return jsonify({"error": "Fields 'old_valor' and 'new_valor' are required."}), 400

    if modo not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    tree = avl_tree if modo == "AVL" else bst_tree
    try:
        target = tree.search(old_value)
    except Exception:
        target = None
    if target is None:
        return jsonify({"error": f"El valor {old_value} no existe en el árbol {modo}."}), 404

    push_history(f"modify-{modo.lower()}")

    # Preserve and align metadata with the new key value when possible.
    metadata = target.getMetadata() if hasattr(target, "getMetadata") else {}
    new_metadata = update_metadata_value(metadata, old_value, new_value)

    tree.delete(old_value)
    tree.insert(Node(new_value, new_metadata))

    if modo == "AVL":
        rebalance_avl_tree()
        arbol = tree_to_dict(avl_tree.root, avl_tree)
    else:
        arbol = tree_to_dict(bst_tree.root, bst_tree)

    return jsonify({"arbol": arbol})


@app.route("/cancel", methods=["POST"])
def cancel_flight_subtree():
    """Cancel a flight by removing target node and all descendants."""
    global avl_tree, bst_tree

    data = request.get_json(silent=True) or {}
    valor = data.get("valor")
    modo = data.get("modo")

    if valor is None:
        return jsonify({"error": "El campo 'valor' es requerido y no puede ser null"}), 400

    if modo not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    tree = avl_tree if modo == "AVL" else bst_tree
    try:
        target = tree.search(valor)
    except Exception:
        target = None
    if target is None:
        return jsonify({"error": f"El valor {valor} no existe en el árbol {modo}."}), 404

    push_history(f"cancel-{modo.lower()}")

    parent = target.getParent()
    if parent is None:
        tree.root = None
    else:
        # Detach the whole subtree in one operation.
        if parent.getLeftChild() == target:
            parent.setLeftChild(None)
        else:
            parent.setRightChild(None)
        target.setParent(None)

    if modo == "AVL":
        rebalance_avl_tree()
        arbol = tree_to_dict(avl_tree.root, avl_tree)
    else:
        arbol = tree_to_dict(bst_tree.root, bst_tree)

    return jsonify({"arbol": arbol})


@app.route("/undo", methods=["POST"])
def undo_action():
    """Restore the latest snapshot to emulate Ctrl+Z behavior."""
    if len(history_stack) == 0:
        return jsonify({"error": "No hay acciones para deshacer."}), 409

    data = request.get_json(silent=True) or {}
    modo = data.get("modo", "AVL")

    record = history_stack.pop()
    restore_state(record["state"])

    if modo == "BST":
        arbol = tree_to_dict(bst_tree.root, bst_tree)
    else:
        arbol = tree_to_dict(avl_tree.root, avl_tree)

    return jsonify({"arbol": arbol, "undone_action": record["action"]})


@app.route("/traversal", methods=["POST"])
def traversal():
    data = request.get_json(silent=True) or {}
    modo = data.get("modo")
    tipo = data.get("tipo")

    tree = avl_tree if modo == "AVL" else bst_tree

    if tipo == "inorder":
        resultado = tree.inOrderTraversal()
    elif tipo == "preorder":
        resultado = tree.preOrderTraversal()
    elif tipo == "postorder":
        resultado = tree.posOrderTraversal()
    elif tipo == "level":
        resultado = tree.breadthFirstSearch()
    else:
        return jsonify({"error": "Tipo de recorrido inválido"}), 400

    # Normalize empty traversal responses when model returns None.
    if resultado is None:
        resultado = []

    # los métodos retornan nodos, extraemos solo los valores
    if tipo == "level":
        valores = resultado  # breadthFirstSearch ya retorna valores
    else:
        valores = [n.getValue() for n in resultado]

    return jsonify({"resultado": valores})


@app.route("/load-json", methods=["POST"])
def load_json():
    """Load trees from user-selected JSON and return AVL/BST comparison data."""
    global avl_tree, bst_tree

    # Parse request safely and default to empty dict.
    data = request.get_json(silent=True) or {}
    json_data = data.get("json_data")
    load_mode = data.get("load_mode")
    key_field = data.get("key_field")

    # Validate required payload field.
    if json_data is None:
        return jsonify({"error": "The field 'json_data' is required."}), 400

    try:
        push_history("load-json")
        # Build both trees according to detected or requested mode.
        result = TreeLoadService.load_both_trees(
            json_data=json_data,
            load_mode=load_mode,
            key_field=key_field,
        )

        # Replace in-memory trees to keep AVL as main operational tree.
        avl_tree = result["avl"]
        bst_tree = result["bst"]

        # Serialize both trees for main canvas and comparison window.
        avl_dict = tree_to_dict(avl_tree.root, avl_tree)
        bst_dict = tree_to_dict(bst_tree.root, bst_tree)

        # Return full response with required properties for both trees.
        return jsonify(
            {
                "arbol": avl_dict,
                "main_avl": avl_dict,
                "comparison": {
                    "avl": avl_dict,
                    "bst": bst_dict,
                },
                "properties": result["properties"],
                "load_mode": result["load_mode"],
                "detected_key": result["detected_key"],
            }
        )
    except ValueError as exc:
        # Return validation problems as client errors.
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:
        # Return generic error to avoid server crashes on malformed inputs.
        return jsonify({"error": f"Unexpected load error: {exc}"}), 500


@app.route("/export-json", methods=["POST"])
def export_tree_json():
    """Export full tree state using real hierarchical structure (not flat lists)."""
    data = request.get_json(silent=True) or {}
    active_mode = data.get("modo", "AVL")

    if active_mode not in {"AVL", "BST"}:
        return jsonify({"error": "El campo 'modo' debe ser 'AVL' o 'BST'"}), 400

    avl_export = {
        "summary": compute_tree_summary_for_export(avl_tree),
        "root": serialize_node_for_export(avl_tree.root, avl_tree),
    }
    bst_export = {
        "summary": compute_tree_summary_for_export(bst_tree),
        "root": serialize_node_for_export(bst_tree.root, bst_tree),
    }

    return jsonify(
        {
            "export_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "active_mode": active_mode,
            "trees": {
                "AVL": avl_export,
                "BST": bst_export,
            },
            "notes": {
                "structure": "Hierarchical tree serialized with left/right child links.",
                "restriction": "Export uses real tree structure, not a flat flight list.",
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
