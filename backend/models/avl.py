# clase AVL para gestión de nodos
from models.node import Node


class AVL:

    # constructor del árbol que se crea inicialmente con una raiz vacía
    def __init__(self):
        self.root = None

    # método de insertar para verificar si no hay raíz
    # cuando no hay raíz, se crea el nodo y se asigna como raiz
    # cuando si hay raiz se procede a insertar llamando a la función privada con la raiz del árbol y el nodo a insertar
    def insert(self, node):
        # verificar si no hay raiz para asignar el nuevo como raiz
        if self.root is None:
            self.root = node
        else:
            self.__insert(self.root, node)

    # Método recursivo para insertar un nodo cuando se tiene raiz en el árbol
    def __insert(self, currentRoot, node):
        if node.getValue() == currentRoot.getValue():
            print(f"El valor del nodo {node.getValue()} ya existe en el árbol.")
        else:
            # se verifica si el valor a insertar es mayor que el actual raiz
            if node.getValue() > currentRoot.getValue():
                # se verifica si existe un hijo derecho
                if currentRoot.getRightChild() is None:
                    # si no tiene hijo derecho, se asigna el nodo como hijo derecho
                    currentRoot.setRightChild(node)
                    # y el nuevo nodo tendrá como padre a la actual raiz
                    node.setParent(currentRoot)
                    # verificar el desbalanceo
                    self.checkBalance(currentRoot)
                else:
                    # ya tiene hijo derecho, entonces se debe procesar la inserción desde el hijo derecho
                    # haciendo el llamado recursivo con ese hijo
                    self.__insert(currentRoot.getRightChild(), node)
            else:
                # el valor del nodo a insertar es menor que el valor de la actual raiz
                # se verifica si tiene hijo izquierdo
                if currentRoot.getLeftChild() is None:
                    # si no tiene se asigna el nodo como hijo izquierdo
                    currentRoot.setLeftChild(node)
                    # y al nuevo nodo se le asigna como padre a la actual raiz
                    node.setParent(currentRoot)
                    # verificar el desbalanceo
                    self.checkBalance(currentRoot)
                else:
                    # si tiene hijo izquierdo, entonces se llama recursivamente por el hijo izquierdo con el nodo a insertar.
                    self.__insert(currentRoot.getLeftChild(), node)

    # Método que permita realizar la búsqueda de un nodo mediante su valor
    # debe seguir la lógica de las reglas de un BST
    def search(self, value):
        # validar si existe una raíz en el árbol
        if self.root is None:
            raise Exception("El árbol no tiene una raíz.")
        else:
            return self.__search(self.root, value)

    # función recursiva para atender la búsqueda
    def __search(self, currentRoot, value):
        # validar si el valor buscado es igual a la raiz actual
        # print(f"El valor del nodo es: {currentRoot.getValue()}")
        # print(f"Comparación: {currentRoot.getValue() == value}" )
        if currentRoot.getValue() == value:
            # si es así se retorna la actual raiz
            return currentRoot
        # sino se valida si se debe ir por la derecha o por la izquierda
        elif value > currentRoot.getValue():
            # si es mayor, se verifica que exista un hijo derecho
            # en caso de no existir se genera
            if currentRoot.getRightChild() is None:
                return None
            else:
                # se pasa la solicitud de búsqueda al hijo derecho
                return self.__search(currentRoot.getRightChild(), value)
        else:
            # si es menor, se verifica que exista un hijo izquierdo
            # en caso de no existir se genera
            if currentRoot.getLeftChild() is None:
                return None
            else:
                # se pasa la solicitud de búsqueda al hijo izquierdo
                return self.__search(currentRoot.getLeftChild(), value)

    # Método para recorrido en anchura
    def breadthFirstSearch(self):
        # verificar si el árbol está vacío
        if self.root is None:
            print("El árbol está vacío.")
        else:
            # se encola la raíz de primera
            queue = [self.root]
            # resultado del recorrido
            result = []
            # mientras existan elementos en la cola (nodos)
            # se debe procesar con: desencolar, imprimir y encolar hijos
            while len(queue) > 0:
                # desencolar
                currentNode = queue.pop(0)
                # imprimir que es agregar al resultado
                result.append(currentNode.getValue())
                # se valida que tenga hijo derecho para encolarlo
                if currentNode.getLeftChild() is not None:
                    queue.append(currentNode.getLeftChild())
                # se valida que tenga hijo izquierdo para encolarlo
                if currentNode.getRightChild() is not None:
                    queue.append(currentNode.getRightChild())
            return result

    # Método para realizar el recorrido en profundidad tipo  Pre-Order
    def preOrderTraversal(self):
        # validar si el árbol está vacío y mostrar mensaje
        if self.root is None:
            print("El árbol está vacío.")
        else:
            # si el árbol no está vacío, se genera un result que tendrá el recorrido al final
            result = []
            # se inicia el llamado recursivo por la raiz del árbol
            self.__preOrderTraversal(self.root, result)
            return result

    # Método recursivo para el recorrido Pre-Order
    def __preOrderTraversal(self, currentRoot, result):
        # Se imprime (agrega a la cola) la raiz actual
        result.append(currentRoot)

        # se verifica si tiene hijo izquierdo para seguir el recorrido por él
        if currentRoot.getLeftChild() is not None:
            self.__preOrderTraversal(currentRoot.getLeftChild(), result)

        # se verifica si tiene hijo derecho para seguir el recorrido por él
        if currentRoot.getRightChild() is not None:
            self.__preOrderTraversal(currentRoot.getRightChild(), result)

    # Método para realizar el recorrido en profundidad tipo  In-Order
    def inOrderTraversal(self):
        # validar si el árbol está vacío y mostrar mensaje
        if self.root is None:
            print("El árbol está vacío.")
        else:
            # si el árbol no está vacío, se genera un result que tendrá el recorrido al final
            result = []
            # se inicia el llamado recursivo por la raiz del árbol
            self.__inOrderTraversal(self.root, result)
            return result

    # Método recursivo para el recorrido Pre-Order
    def __inOrderTraversal(self, currentRoot, result):
        # se verifica si tiene hijo izquierdo para seguir el recorrido por él
        if currentRoot.getLeftChild() is not None:
            self.__inOrderTraversal(currentRoot.getLeftChild(), result)

        # Se imprime (agrega a la cola) la raiz actual
        result.append(currentRoot)

        # se verifica si tiene hijo derecho para seguir el recorrido por él
        if currentRoot.getRightChild() is not None:
            self.__inOrderTraversal(currentRoot.getRightChild(), result)

    # Método para realizar el recorrido en profundidad tipo  Pos-Order
    def posOrderTraversal(self):
        # validar si el árbol está vacío y mostrar mensaje
        if self.root is None:
            print("El árbol está vacío.")
        else:
            # si el árbol no está vacío, se genera un result que tendrá el recorrido al final
            result = []
            # se inicia el llamado recursivo por la raiz del árbol
            self.__posOrderTraversal(self.root, result)
            return result

    # Método recursivo para el recorrido Pre-Order
    def __posOrderTraversal(self, currentRoot, result):
        # se verifica si tiene hijo izquierdo para seguir el recorrido por él
        if currentRoot.getLeftChild() is not None:
            self.__posOrderTraversal(currentRoot.getLeftChild(), result)

        # se verifica si tiene hijo derecho para seguir el recorrido por él
        if currentRoot.getRightChild() is not None:
            self.__posOrderTraversal(currentRoot.getRightChild(), result)

        # Se imprime (agrega a la cola) la raiz actual
        result.append(currentRoot)

    # Método para eliminar
    def delete(self, value):
        if self.root is None:
            print("El árbol está vacío.")
            return

        node = self.__search(self.root, value)

        if node is None:
            print(f"El valor {value} no se encuentra en el árbol.")
        else:
            self.__deleteNode(node)

    # Método que evalúa cada uno de los casos de eliminar y procede según sea
    def __deleteNode(self, node):
        # identificar el caso de eliminación
        nodeCase = self.IdentifyDeletionCase(node)
        match nodeCase:
            case 1:
                self.__deleteLeafNode(node)
            case 2:
                self.__deleteNodeWithOneChild(node)
            case 3:
                self.__deleteNodeWithTwoChildren(node)

    # Metodo que permite eliminar un nodo hoja
    def __deleteLeafNode(self, node):
        if node == self.root:
            self.root = None
            return

        if node.getValue() < node.getParent().getValue():
            node.getParent().setLeftChild(None)
        else:
            node.getParent().setRightChild(None)
        node.setParent(None)

    # Metodo que permite eliminar un nodo con un hijo
    def __deleteNodeWithOneChild(self, node):
        # Determinar cuál es el hijo que sobrevive
        if node.getLeftChild() is None:
            child = node.getRightChild()
        else:
            child = node.getLeftChild()

        parent = node.getParent()

        # Actualizar el padre del hijo
        child.setParent(parent)

        # Actualizar el puntero del padre hacia el hijo
        if parent is not None:
            if parent.getLeftChild() == node:
                parent.setLeftChild(child)
            else:
                parent.setRightChild(child)
        else:
            # El nodo eliminado era la raíz
            self.root = child

        # Desconectar el nodo eliminado
        node.setParent(None)
        node.setLeftChild(None)
        node.setRightChild(None)

    # Metodo que permite eliminar un nodo con dos hijos
    def __deleteNodeWithTwoChildren(self, node):
        # 1. Encontrar el predecesor (máximo del subárbol izquierdo)
        predecessor = node.getLeftChild()
        while predecessor.getRightChild() is not None:
            predecessor = predecessor.getRightChild()

        # 2. Copiar el valor del predecesor al nodo a eliminar
        node.setValue(predecessor.getValue())

        # 3. Eliminar el predecesor (que tiene 0 o 1 hijo)
        if predecessor.getRightChild() is None and predecessor.getLeftChild() is None:
            self.__deleteLeafNode(predecessor)
        else:
            self.__deleteNodeWithOneChild(predecessor)

    # Metodo par identificar cual es el caso de eliminación
    # 1. Nodo hoja
    # 2. Nodo con un hijo
    # 3. Nodo con dos hijos
    def IdentifyDeletionCase(self, node):
        nodeCase = 2
        if node.getLeftChild() is None and node.getRightChild() is None:
            nodeCase = 1
        elif node.getLeftChild() is not None and node.getRightChild() is not None:
            nodeCase = 3
        return nodeCase

    # Metodo para calcular la altura de un nodo
    def getHeightNode(self, node):
        if node is None:
            return 0
        else:
            return self.__getHeightNode(node)

    # Metodo recursivo para calcular la altura de un nodo
    def __getHeightNode(self, node):
        # Si el nodo es none, se retorna -1 para equilibrar el +1 de su padre y así el nodo hoja tendrá altura 0
        if node is None:
            return -1
        else:
            # se obtiene la altura del hijo izquierdo y del hijo derecho
            leftHeight = self.__getHeightNode(node.getLeftChild())
            # se obtiene la altura del hijo derecho
            rightHeight = self.__getHeightNode(node.getRightChild())
            # se incrementa en 1 al retornar a al padre para contar el nivel del nodo actual
            maxHeight = max(leftHeight, rightHeight)
            # se incrementa en 1 al retornar al padre para representar la arista que los une
            return maxHeight + 1

    # INICIO DE METODOS DEL BALANCEO DEL ÁRBOL
    # ------------------------------------------------------------------------------

    # Metodo para checar el balanceo de un arabol a partir de un nodo
    def checkBalance(self, node):
        if node is None:
            raise Exception("El nodo a balancear no es valido.")
        elif node != self.root:
            self.__checkBalance(node)

    # Metodo recursivo para checar el balanceo de un arabol a partir de un arbol
    def __checkBalance(self, node):
        bf = self.getBalanceFactor(node)
        if bf > 1 or bf < -1:
            # se identifica el caso de desbalanceo (LL, LR, RR, RL)
            bfCase = self.getBalanceCase(node, bf)
            match bfCase:
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
        else:
            # se verifica que el nodo acctual no sea la raiz, y se invoca el checeo del balanceo para el nodo padre
            # cuando es la raiz se finaliza la evaluación
            if node != self.root:
                # if node.getParent() is not None: (no sirvio)
                self.__checkBalance(node.getParent())

    # Metodo para hacer el giro simple a la derecha
    def __rotateRight(self, topNode):
        # se obtiene el nodo de la mitad
        middleNode = topNode.getLeftChild()

        # se obtiene el padre del nodo superior, cuando ees la raiz sera none
        parentTopNode = topNode.getParent()

        # se obtiene el hijo derecho del nodo de la mitad
        rightChildOfMiddleNode = middleNode.getRightChild()

        # se mueve el superior como hijo derecho del nodo de la mitad
        middleNode.setRightChild(topNode)
        topNode.setParent(middleNode)

        # reacomodoar al nodo padre del superior apuntando al de la mitad
        # verificar si el superior era la raiz
        if parentTopNode is None:
            self.root = middleNode
            middleNode.setParent(None)
        else:
            if parentTopNode.getLeftChild() == topNode:
                parentTopNode.setLeftChild(middleNode)
            else:
                parentTopNode.setRightChild(middleNode)
            # sin importar si era hijo izq o derecho, se asigna ese padre del superior como padre del nodo de la mitad
            middleNode.setParent(parentTopNode)
        # reasignar el hijo derecho del nodo de la mitad al nodo superior
        topNode.setLeftChild(rightChildOfMiddleNode)
        if rightChildOfMiddleNode is not None:
            rightChildOfMiddleNode.setParent(topNode)

    # método para el giro simple a la izquierda
    def __rotateLeft(self, topNode):
        # se obtiene el nodo de la mitad
        middleNode = topNode.getRightChild()

        # se obtiene el padre del nodo superior, cuando es la raiz será None
        parentTopNode = topNode.getParent()

        # se obtiene el hijo izquierdo del nodo de la mitad
        leftChildOfMiddleNode = middleNode.getLeftChild()

        # se mueve el superior como hijo izquierdo del nodo de la mitad
        middleNode.setLeftChild(topNode)
        topNode.setParent(middleNode)

        # reacomodar al nodo padre del superior apuntando al de la mitad
        # verificar si el superior era la raiz
        if parentTopNode is None:
            self.root = middleNode
            middleNode.setParent(None)
        else:
            if parentTopNode.getLeftChild() == topNode:
                parentTopNode.setLeftChild(middleNode)
            else:
                parentTopNode.setRightChild(middleNode)
            # sin importar si era hijo izq o derecho, se asigna ese padre del superior como padre del nodo de la mitad
            middleNode.setParent(parentTopNode)

        # reasignar el hijo izquierdo del nodo de la mitad al nodo superior que ya bajó como hijo izquierdo del nodo de la mitad
        topNode.setRightChild(leftChildOfMiddleNode)
        if leftChildOfMiddleNode is not None:
            leftChildOfMiddleNode.setParent(topNode)

    # metodo para identificar el caso de desbalanceo
    def getBalanceCase(self, node, bf):
        bfCase = ""
        # caso negativo, va por R
        if bf < -1:
            bfChild = self.getBalanceFactor(node.getRightChild())
            # caso negativo, va por R
            if bfChild <= 0:
                bfCase = "RR"
            else:
                bfCase = "RL"
        # caso positivo, va por L
        else:
            bfChild = self.getBalanceFactor(node.getLeftChild())
            # caso positivo, va por L
            if bfChild >= 0:
                bfCase = "LL"
            else:
                bfCase = "LR"
        return bfCase

    # Metodo para calcular el BF de un nodo
    def getBalanceFactor(self, node):
        if node is None:
            return 0
        else:
            leftChildHeight = self.__getHeightNode(node.getLeftChild())
            rightChildHeight = self.__getHeightNode(node.getRightChild())
            return leftChildHeight - rightChildHeight

    # ------------------------------------------------------------------------------
    # FIN DE MÉTODOS DEL BALANCEO DEL ÁRBOL AVL

    # Método para dibujar el árbol en forma de árbol
    def print_tree(self):
        if self.root is None:
            print("El árbol está vacío.")
        else:
            self.__print_tree(self.root, "", True)

    # Methodo para imprimir el árbol BST
    def __print_tree(self, node=None, prefix="", is_left=True):
        if node is not None:
            # Print right subtree
            if node.getRightChild():
                new_prefix = prefix + ("│   " if is_left else "    ")
                self.__print_tree(node.getRightChild(), new_prefix, False)

            # Print current node
            connector = "└── " if is_left else "┌── "
            print(prefix + connector + str(node.getValue()))

            # Print left subtree
            if node.getLeftChild():
                new_prefix = prefix + ("    " if is_left else "│   ")
                self.__print_tree(node.getLeftChild(), new_prefix, True)
