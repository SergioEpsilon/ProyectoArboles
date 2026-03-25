"""Base class for tree implementations (BST, AVL).

Encapsulates common tree operations to eliminate duplication between BST and AVL.
Single Responsibility: Provides shared recursive tree algorithms.
"""

from models.node import Node


class BaseTree:
    """Abstract base class for binary search trees.

    Provides: insert, search, delete, traversals (BFS, preorder, inorder, postorder).
    Subclasses override: __init__ to set metrics service, checkBalance() for balance logic.
    """

    def __init__(self):
        """Initialize empty tree. Subclasses may add metrics_service parameter."""
        self.root = None

    # ─── Insertion & Search ───────────────────────────────────────────────────

    def insert(self, node: Node) -> None:
        """Insert a node into the tree."""
        if self.root is None:
            self.root = node
        else:
            self.__insert(self.root, node)

    def __insert(self, current_root: Node, node: Node) -> None:
        """Recursive insertion. Subclasses may override to inject balance logic."""
        if node.getValue() == current_root.getValue():
            print(f"El valor del nodo {node.getValue()} ya existe en el árbol.")
            return

        if node.getValue() > current_root.getValue():
            if current_root.getRightChild() is None:
                current_root.setRightChild(node)
                node.setParent(current_root)
                self._post_insert(current_root)  # Hook for balance logic
            else:
                self.__insert(current_root.getRightChild(), node)
        else:
            if current_root.getLeftChild() is None:
                current_root.setLeftChild(node)
                node.setParent(current_root)
                self._post_insert(current_root)  # Hook for balance logic
            else:
                self.__insert(current_root.getLeftChild(), node)

    def _post_insert(self, node: Node) -> None:
        """Hook for subclasses to add balance logic (AVL). Base class does nothing."""
        pass

    def search(self, value) -> Node | None:
        """Search for a node by value. Returns None if not found."""
        if self.root is None:
            raise Exception("El árbol no tiene una raíz.")
        return self.__search(self.root, value)

    def __search(self, current_root: Node, value) -> Node | None:
        """Recursive search using BST ordering."""
        if current_root.getValue() == value:
            return current_root
        elif value > current_root.getValue():
            return None if current_root.getRightChild() is None else self.__search(current_root.getRightChild(), value)
        else:
            return None if current_root.getLeftChild() is None else self.__search(current_root.getLeftChild(), value)

    # ─── Deletion ─────────────────────────────────────────────────────────────

    def delete(self, value) -> None:
        """Delete a node by value from the tree."""
        if self.root is None:
            print("El árbol está vacío.")
            return

        node = self.__search(self.root, value)
        if node is None:
            print(f"El valor {value} no se encuentra en el árbol.")
        else:
            self.__delete_node(node)

    def __delete_node(self, node: Node) -> None:
        """Delete a node, handling three cases: leaf, one child, two children."""
        # Leaf node
        if node.getLeftChild() is None and node.getRightChild() is None:
            self._remove_from_parent(node)
            return

        # One child
        if node.getLeftChild() is None or node.getRightChild() is None:
            child = node.getLeftChild() if node.getLeftChild() is not None else node.getRightChild()
            self._replace_node(node, child)
            return

        # Two children: find inorder successor
        successor = self._find_successor(node.getRightChild())
        node.setData(successor.getData())
        self.__delete_node(successor)

    def _find_successor(self, node: Node) -> Node:
        """Find the node with minimum value in a subtree."""
        while node.getLeftChild() is not None:
            node = node.getLeftChild()
        return node

    def _remove_from_parent(self, node: Node) -> None:
        """Detach a leaf node from its parent."""
        if node.getParent() is None:
            self.root = None
        elif node.getParent().getLeftChild() == node:
            node.getParent().setLeftChild(None)
        else:
            node.getParent().setRightChild(None)

    def _replace_node(self, old_node: Node, new_node: Node | None) -> None:
        """Replace a node with another (potentially None)."""
        if old_node.getParent() is None:
            self.root = new_node
        elif old_node.getParent().getLeftChild() == old_node:
            old_node.getParent().setLeftChild(new_node)
        else:
            old_node.getParent().setRightChild(new_node)

        if new_node is not None:
            new_node.setParent(old_node.getParent())

    # ─── Traversals ───────────────────────────────────────────────────────────

    def breadth_first_search(self) -> list:
        """Level-order traversal (BFS)."""
        if self.root is None:
            return []
        queue = [self.root]
        result = []
        while queue:
            current = queue.pop(0)
            result.append(current.getValue())
            if current.getLeftChild() is not None:
                queue.append(current.getLeftChild())
            if current.getRightChild() is not None:
                queue.append(current.getRightChild())
        return result

    def pre_order_traversal(self) -> list:
        """Root → Left → Right."""
        if self.root is None:
            return []
        result = []
        self.__pre_order(self.root, result)
        return result

    def __pre_order(self, node: Node, result: list) -> None:
        """Recursive pre-order helper."""
        result.append(node)
        if node.getLeftChild() is not None:
            self.__pre_order(node.getLeftChild(), result)
        if node.getRightChild() is not None:
            self.__pre_order(node.getRightChild(), result)

    def in_order_traversal(self) -> list:
        """Left → Root → Right."""
        if self.root is None:
            return []
        result = []
        self.__in_order(self.root, result)
        return result

    def __in_order(self, node: Node, result: list) -> None:
        """Recursive in-order helper."""
        if node.getLeftChild() is not None:
            self.__in_order(node.getLeftChild(), result)
        result.append(node)
        if node.getRightChild() is not None:
            self.__in_order(node.getRightChild(), result)

    def post_order_traversal(self) -> list:
        """Left → Right → Root."""
        if self.root is None:
            return []
        result = []
        self.__post_order(self.root, result)
        return result

    def __post_order(self, node: Node, result: list) -> None:
        """Recursive post-order helper."""
        if node.getLeftChild() is not None:
            self.__post_order(node.getLeftChild(), result)
        if node.getRightChild() is not None:
            self.__post_order(node.getRightChild(), result)
        result.append(node)

    # ─── Utility (Backward Compatibility) ──────────────────────────────────────

    def breadthFirstSearch(self):
        """Deprecated: Use breadth_first_search()."""
        return self.breadth_first_search()

    def preOrderTraversal(self):
        """Deprecated: Use pre_order_traversal()."""
        return self.pre_order_traversal()

    def inOrderTraversal(self):
        """Deprecated: Use in_order_traversal()."""
        return self.in_order_traversal()

    def posOrderTraversal(self):
        """Deprecated: Use post_order_traversal()."""
        return self.post_order_traversal()
