# clase que permite instanciar nuevos nodos con sus atributos
class Node:

    # constructor para el nodo con hijos, padre y valor
    def __init__(self, value, metadata=None):
        # Store the comparable value used by BST/AVL ordering.
        self.value = value
        # Store original JSON payload for future features and rich rendering.
        self.metadata = metadata if metadata is not None else {}
        # Initialize linkage attributes for tree structure.
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

    # asignar el valor del nodo
    def setValue(self, value):
        self.value = value

    # assign metadata for this node
    def setMetadata(self, metadata):
        # Keep metadata as dictionary-like payload to preserve source JSON info.
        self.metadata = metadata if metadata is not None else {}

    # return metadata for this node
    def getMetadata(self):
        return self.metadata

    # Compatibilidad con implementaciones antiguas
    def getData(self):
        return self.getValue()

    # Compatibilidad con implementaciones antiguas
    def setData(self, value):
        self.setValue(value)
