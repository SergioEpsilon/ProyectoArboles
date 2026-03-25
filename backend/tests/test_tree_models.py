"""Unit tests for optimized tree model classes."""

import unittest

from models.avl import AVL
from models.bst import BST
from models.node import Node


class BaseTreeContractMixin:
    """Shared assertions for BST/AVL behavior."""

    TREE_CLASS = None

    def build_tree(self, values):
        tree = self.TREE_CLASS()
        for value in values:
            tree.insert(Node(value, {"value": value}))
        return tree

    def test_search_existing_and_missing(self):
        tree = self.build_tree([40, 20, 60, 10, 30, 50, 70])
        self.assertEqual(tree.search(30).getValue(), 30)
        self.assertIsNone(tree.search(999))

    def test_inorder_traversal_sorted(self):
        tree = self.build_tree([40, 20, 60, 10, 30, 50, 70])
        nodes = tree.inOrderTraversal()
        self.assertEqual([n.getValue() for n in nodes], [10, 20, 30, 40, 50, 60, 70])

    def test_breadth_first_traversal_root_first(self):
        tree = self.build_tree([40, 20, 60])
        self.assertEqual(tree.breadthFirstSearch(), [40, 20, 60])

    def test_delete_leaf_node(self):
        tree = self.build_tree([40, 20, 60, 10])
        tree.delete(10)
        self.assertIsNone(tree.search(10))

    def test_delete_node_with_one_child(self):
        tree = self.build_tree([40, 20, 60, 10])
        tree.delete(20)
        self.assertIsNone(tree.search(20))
        self.assertEqual(tree.search(10).getParent().getValue(), 40)


class TestBST(BaseTreeContractMixin, unittest.TestCase):
    TREE_CLASS = BST

    def test_height_empty_and_non_empty(self):
        tree = BST()
        self.assertEqual(tree.getHeightNode(tree.root), 0)
        tree.insert(Node(5, {}))
        self.assertEqual(tree.getHeightNode(tree.root), 0)


class TestAVL(BaseTreeContractMixin, unittest.TestCase):
    TREE_CLASS = AVL

    def test_ll_rotation_balances_tree(self):
        tree = AVL()
        tree.insert(Node(30, {}))
        tree.insert(Node(20, {}))
        tree.insert(Node(10, {}))
        self.assertEqual(tree.root.getValue(), 20)
        self.assertEqual(tree.getBalanceFactor(tree.root), 0)


if __name__ == "__main__":
    unittest.main()
