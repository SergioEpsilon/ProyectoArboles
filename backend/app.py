from flask import Flask, request, jsonify
from flask_cors import CORS
from models.node import Node
from models.avl import AVL
from models.bst import BST
from services.tree_service import TreeLoadService

app = Flask(__name__)
CORS(app)  # permite que el HTML se comunique con Flask

# Estado del árbol en memoria
avl_tree = AVL()
bst_tree = BST()


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
        avl_tree.insert(node)
        arbol = tree_to_dict(avl_tree.root, avl_tree)
    else:
        bst_tree.insert(node)
        arbol = tree_to_dict(bst_tree.root, bst_tree)

    return jsonify({"arbol": arbol})


# Endpoint para limpiar el árbol
@app.route("/clear", methods=["POST"])
def clear():
    global avl_tree, bst_tree
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
        avl_tree.delete(valor)
        arbol = tree_to_dict(avl_tree.root, avl_tree)
    else:
        bst_tree.delete(valor)
        arbol = tree_to_dict(bst_tree.root, bst_tree)

    return jsonify({"arbol": arbol})


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


if __name__ == "__main__":
    app.run(debug=True)
