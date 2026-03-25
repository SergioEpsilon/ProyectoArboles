"""Service for tracking and computing real-time tree metrics.

Maintains counters for rotations, cancellations, and computes structural
properties like height, leaf count, traversals.
"""

from __future__ import annotations

from typing import Any, Dict, List

from models.avl import AVL
from models.bst import BST
from models.node import Node


class MetricsService:
    """Tracks tree transformations and computes structural metrics.

    Single Responsibility: manages metric collection and computation.
    Does not modify trees—only observes and counts.
    """

    def __init__(self) -> None:
        """Initialize metrics service with zero counters."""
        self._rotation_counts: Dict[str, int] = {
            "LL": 0,
            "LR": 0,
            "RR": 0,
            "RL": 0,
        }
        self._cancellation_count = 0

    def record_rotation(self, rotation_type: str) -> None:
        """Record a single rotation event.

        Args:
            rotation_type: One of 'LL', 'LR', 'RR', 'RL'.
        """
        if rotation_type in self._rotation_counts:
            self._rotation_counts[rotation_type] += 1

    def record_cancellation(self) -> None:
        """Record a single node + subtree cancellation event."""
        self._cancellation_count += 1

    def reset_counters(self) -> None:
        """Reset all rotation and cancellation counters to zero."""
        self._rotation_counts = {"LL": 0, "LR": 0, "RR": 0, "RL": 0}
        self._cancellation_count = 0

    def get_rotation_stats(self) -> Dict[str, int]:
        """Return current rotation counts by type."""
        return dict(self._rotation_counts)

    def get_cancellation_count(self) -> int:
        """Return total cancellation count."""
        return self._cancellation_count

    @staticmethod
    def compute_height(tree: AVL | BST) -> int:
        """Compute current tree height."""
        if tree.root is None:
            return 0
        return tree.getHeightNode(tree.root)

    @staticmethod
    def compute_node_count(node: Node | None) -> int:
        """Count total nodes in subtree recursively."""
        if node is None:
            return 0
        left_count = MetricsService.compute_node_count(node.getLeftChild())
        right_count = MetricsService.compute_node_count(node.getRightChild())
        return 1 + left_count + right_count

    @staticmethod
    def compute_leaf_count(node: Node | None) -> int:
        """Count leaf nodes (nodes with no children) recursively."""
        if node is None:
            return 0
        is_leaf = node.getLeftChild() is None and node.getRightChild() is None
        if is_leaf:
            return 1
        left_leaves = MetricsService.compute_leaf_count(node.getLeftChild())
        right_leaves = MetricsService.compute_leaf_count(node.getRightChild())
        return left_leaves + right_leaves

    @staticmethod
    def compute_balance_factor(tree: AVL | BST) -> int:
        """Compute balance factor of root node.

        For AVL: left_height - right_height.
        For BST: approximation using same formula.
        """
        if tree.root is None:
            return 0

        if isinstance(tree, AVL):
            return tree.getBalanceFactor(tree.root)

        left_h = tree.getHeightNode(tree.root.getLeftChild())
        right_h = tree.getHeightNode(tree.root.getRightChild())
        return left_h - right_h

    @staticmethod
    def all_metrics(tree: AVL | BST) -> Dict[str, Any]:
        """Compute all structural metrics for current tree state."""
        height = MetricsService.compute_height(tree)
        node_count = MetricsService.compute_node_count(tree.root)
        leaf_count = MetricsService.compute_leaf_count(tree.root)
        balance_factor = MetricsService.compute_balance_factor(tree)

        return {
            "height": height,
            "nodes": node_count,
            "leaves": leaf_count,
            "balance_factor": balance_factor,
        }
