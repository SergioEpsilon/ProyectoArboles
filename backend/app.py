from flask import Flask, request, jsonify
from flask_cors import CORS
from models.node import Node
from models.avl import AVL
from models.bst import BST

app = Flask(__name__)
CORS(app)  # permite que el HTML se comunique con Flask

# Estado del árbol en memoria
avl_tree = AVL()
bst_tree = BST()


# Función que convierte el árbol a un diccionario para enviarlo al frontend
def tree_to_dict(node):
    if node is None:
        return None
    return {
        "val": node.getValue(),
        "left": tree_to_dict(node.getLeftChild()),
        "right": tree_to_dict(node.getRightChild()),
        "height": avl_tree.getHeightNode(node),
    }


# Endpoint para insertar un nodo
@app.route("/insert", methods=["POST"])
def insert():
    data = request.get_json()
    valor = data.get("valor")
    modo = data.get("modo")  # 'AVL' o 'BST'

    node = Node(valor)

    if modo == "AVL":
        avl_tree.insert(node)
        arbol = tree_to_dict(avl_tree.root)
    else:
        bst_tree.insert(node)
        arbol = tree_to_dict(bst_tree.root)

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
    data = request.get_json()
    valor = data.get("valor")
    modo = data.get("modo")

    if modo == "AVL":
        avl_tree.delete(valor)
        arbol = tree_to_dict(avl_tree.root)
    else:
        bst_tree.delete(valor)
        arbol = tree_to_dict(bst_tree.root)

    return jsonify({"arbol": arbol})


@app.route("/traversal", methods=["POST"])
def traversal():
    data = request.get_json()
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

    # los métodos retornan nodos, extraemos solo los valores
    if tipo == "level":
        valores = resultado  # breadthFirstSearch ya retorna valores
    else:
        valores = [n.getValue() for n in resultado]

    return jsonify({"resultado": valores})


if __name__ == "__main__":
    app.run(debug=True)
