"""Unit tests for TreeLoadService optimizations."""

import unittest

from services.tree_service import TreeLoadService


class TestTreeLoadService(unittest.TestCase):
    def test_extract_insertion_items_accepts_multiple_wrappers(self):
        self.assertEqual(TreeLoadService._extract_insertion_items({"vuelos": [1, 2]}), [1, 2])
        self.assertEqual(TreeLoadService._extract_insertion_items({"nodes": [3, 4]}), [3, 4])
        self.assertEqual(TreeLoadService._extract_insertion_items({"items": [5, 6]}), [5, 6])

    def test_count_nodes_and_leaves_empty(self):
        nodes, leaves = TreeLoadService._count_nodes_and_leaves(None)
        self.assertEqual(nodes, 0)
        self.assertEqual(leaves, 0)


if __name__ == "__main__":
    unittest.main()
