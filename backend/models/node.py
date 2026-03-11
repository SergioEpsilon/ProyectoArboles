# clase que permite instanciar nuevos nodos con sus atributos
class Node:

    # constructor para el nodo con hijos, padre y valor
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.leftChild = None
        self.rightChild = None

    # asignación de un hijo derecho
    def setRightChild(self, node):
        self.rightChild = node

    # obtener el hijo derecho
    def getRightChild(self):
        return self.rightChild

    # asignar un hijo izquierdo
    def setLeftChild(self, node):
        self.leftChild = node

    # obtener el hijo izquiero
    def getLeftChild(self):
        return self.leftChild

    # asignar un padre
    def setParent(self, node):
        self.parent = node

    # obtener el nodo padre
    def getParent(self):
        return self.parent

    # obtener el valor del nodo
    def getValue(self):
        return self.value
