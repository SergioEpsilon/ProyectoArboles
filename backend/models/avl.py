# clase AVL para gestion de nodos
from __future__ import annotations

from typing import TYPE_CHECKING

from models.base_tree import BaseTree
from models.tree_printer import print_ascii_tree

if TYPE_CHECKING:
    from services.metrics_service import MetricsService


class AVL(BaseTree):
    """AVL self-balancing binary search tree."""

    def __init__(self, metrics_service: MetricsService | None = None):
        super().__init__()
        self._metrics = metrics_service

    # Metodo para calcular la altura de un nodo
    def getHeightNode(self, node):
        if node is None:
            return 0
        return self.__getHeightNode(node)

    # Metodo recursivo para calcular la altura de un nodo
    def __getHeightNode(self, node):
        # Si el nodo es none, se retorna -1 para equilibrar el +1 de su padre
        if node is None:
            return -1

        left_height = self.__getHeightNode(node.getLeftChild())
        right_height = self.__getHeightNode(node.getRightChild())
        return max(left_height, right_height) + 1

    # Hook de BaseTree: balancea despues de insertar en el padre inmediato
    def _post_insert(self, node) -> None:
        self.checkBalance(node)

    # Metodo para checar el balanceo de un arbol a partir de un nodo
    def checkBalance(self, node):
        if node is None:
            raise Exception("El nodo a balancear no es valido.")
        if node != self.root:
            self.__checkBalance(node)

    # Metodo recursivo para checar el balanceo
    def __checkBalance(self, node):
        bf = self.getBalanceFactor(node)
        if bf > 1 or bf < -1:
            bf_case = self.getBalanceCase(node, bf)
            if self._metrics is not None:
                self._metrics.record_rotation(bf_case)

            match bf_case:
                case "LL":
                    self.__rotateRight(node)
                case "RR":
                    self.__rotateLeft(node)
                case "LR":
                    self.__rotateLeft(node.getLeftChild())
                    self.__rotateRight(node)
                case "RL":
                    self.__rotateRight(node.getRightChild())
                    self.__rotateLeft(node)
        elif node != self.root:
            self.__checkBalance(node.getParent())

    # Metodo para hacer giro simple a la derecha
    def __rotateRight(self, topNode):
        middle_node = topNode.getLeftChild()
        parent_top_node = topNode.getParent()
        right_child_of_middle = middle_node.getRightChild()

        middle_node.setRightChild(topNode)
        topNode.setParent(middle_node)

        if parent_top_node is None:
            self.root = middle_node
            middle_node.setParent(None)
        else:
            if parent_top_node.getLeftChild() == topNode:
                parent_top_node.setLeftChild(middle_node)
            else:
                parent_top_node.setRightChild(middle_node)
            middle_node.setParent(parent_top_node)

        topNode.setLeftChild(right_child_of_middle)
        if right_child_of_middle is not None:
            right_child_of_middle.setParent(topNode)

    # Metodo para el giro simple a la izquierda
    def __rotateLeft(self, topNode):
        middle_node = topNode.getRightChild()
        parent_top_node = topNode.getParent()
        left_child_of_middle = middle_node.getLeftChild()

        middle_node.setLeftChild(topNode)
        topNode.setParent(middle_node)

        if parent_top_node is None:
            self.root = middle_node
            middle_node.setParent(None)
        else:
            if parent_top_node.getLeftChild() == topNode:
                parent_top_node.setLeftChild(middle_node)
            else:
                parent_top_node.setRightChild(middle_node)
            middle_node.setParent(parent_top_node)

        topNode.setRightChild(left_child_of_middle)
        if left_child_of_middle is not None:
            left_child_of_middle.setParent(topNode)

    # Metodo para identificar el caso de desbalanceo
    def getBalanceCase(self, node, bf):
        if bf < -1:
            bf_child = self.getBalanceFactor(node.getRightChild())
            return "RR" if bf_child <= 0 else "RL"

        bf_child = self.getBalanceFactor(node.getLeftChild())
        return "LL" if bf_child >= 0 else "LR"

    # Metodo para calcular el BF de un nodo
    def getBalanceFactor(self, node):
        if node is None:
            return 0
        left_height = self.__getHeightNode(node.getLeftChild())
        right_height = self.__getHeightNode(node.getRightChild())
        return left_height - right_height

    # Metodo para dibujar el arbol
    def print_tree(self):
        print_ascii_tree(self.root)
