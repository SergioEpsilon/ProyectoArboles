# clase BST para gestion de nodos
from models.base_tree import BaseTree
from models.tree_printer import print_ascii_tree


class BST(BaseTree):
    """Binary Search Tree sin auto-balanceo."""

    def __init__(self):
        super().__init__()

    # Metodo para calcular la altura de un nodo
    def getHeightNode(self, node):
        if node is None:
            return 0
        return self.__getHeightNode(node)

    # Metodo recursivo para calcular la altura de un nodo
    def __getHeightNode(self, node):
        if node is None:
            return -1

        left_height = self.__getHeightNode(node.getLeftChild())
        right_height = self.__getHeightNode(node.getRightChild())
        return max(left_height, right_height) + 1

    # Metodo para dibujar el arbol en consola
    def print_tree(self):
        print_ascii_tree(self.root)
