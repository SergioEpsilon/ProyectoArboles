"""Service responsible for serializing and deserializing tree state.

Handles three concerns under one cohesive responsibility:
  - Converting trees to dicts for the frontend (to_dict).
  - Creating/restoring snapshots for undo and versioning.
  - Serializing trees for JSON export.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional

from models.avl import AVL
from models.bst import BST
from models.node import Node
from services.tree_service import TreeLoadService


class TreeSerializer:
    """Converts tree nodes to/from dictionaries for frontend, snapshots, and export."""

    # ── Frontend rendering ────────────────────────────────────────────────────

    @staticmethod
    def to_dict(node, tree) -> Optional[Dict[str, Any]]:
        """Convert a tree node to a dict for the frontend canvas."""
        if node is None:
            return None
        metadata = node.getMetadata() if hasattr(node, "getMetadata") else {}
        return {
            "val": node.getValue(),
            "left": TreeSerializer.to_dict(node.getLeftChild(), tree),
            "right": TreeSerializer.to_dict(node.getRightChild(), tree),
            "height": tree.getHeightNode(node),
            "data": metadata,
        }

    # ── Snapshot / restore ────────────────────────────────────────────────────

    @staticmethod
    def snapshot_node(node) -> Optional[Dict[str, Any]]:
        """Serialize a single node subtree for snapshot storage."""
        if node is None:
            return None
        metadata = node.getMetadata() if hasattr(node, "getMetadata") else {}
        return {
            "val": node.getValue(),
            "data": deepcopy(metadata),
            "left": TreeSerializer.snapshot_node(node.getLeftChild()),
            "right": TreeSerializer.snapshot_node(node.getRightChild()),
        }

    @staticmethod
    def snapshot_state(avl_tree, bst_tree) -> Dict[str, Any]:
        """Create a full snapshot of both AVL and BST trees."""
        return {
            "avl": TreeSerializer.snapshot_node(avl_tree.root),
            "bst": TreeSerializer.snapshot_node(bst_tree.root),
        }

    @staticmethod
    def build_node_from_snapshot(node_payload, parent=None):
        """Rebuild linked Node objects from a serialized snapshot payload."""
        if node_payload is None:
            return None
        node = Node(node_payload.get("val"), deepcopy(node_payload.get("data") or {}))
        node.setParent(parent)
        left = TreeSerializer.build_node_from_snapshot(node_payload.get("left"), node)
        right = TreeSerializer.build_node_from_snapshot(node_payload.get("right"), node)
        node.setLeftChild(left)
        node.setRightChild(right)
        return node

    @staticmethod
    def restore_state(state: Dict[str, Any]):
        """Rebuild AVL and BST trees from a snapshot dict.

        Returns:
            Tuple (avl_tree, bst_tree) with freshly reconstructed trees.
        """
        avl_tree = AVL()
        bst_tree = BST()
        avl_tree.root = TreeSerializer.build_node_from_snapshot(state.get("avl"))
        bst_tree.root = TreeSerializer.build_node_from_snapshot(state.get("bst"))
        return avl_tree, bst_tree

    # ── AVL rebalance helper ──────────────────────────────────────────────────

    @staticmethod
    def collect_values_with_metadata(node, result=None):
        """Collect node values and metadata in pre-order for AVL rebuild."""
        if result is None:
            result = []
        if node is None:
            return result
        metadata = node.getMetadata() if hasattr(node, "getMetadata") else {}
        result.append({"value": node.getValue(), "metadata": deepcopy(metadata)})
        TreeSerializer.collect_values_with_metadata(node.getLeftChild(), result)
        TreeSerializer.collect_values_with_metadata(node.getRightChild(), result)
        return result

    @staticmethod
    def rebalance_avl(avl_tree) -> AVL:
        """Rebuild AVL from its current values to guarantee balance.

        Returns:
            A new, fully balanced AVL tree instance.
        """
        values = TreeSerializer.collect_values_with_metadata(avl_tree.root)
        rebuilt = AVL()
        for item in values:
            rebuilt.insert(Node(item["value"], item["metadata"]))
        return rebuilt

    # ── Metadata helpers ──────────────────────────────────────────────────────

    @staticmethod
    def get_metadata_value(metadata, keys, default=None):
        """Read the first available metadata field from multiple key aliases."""
        if not isinstance(metadata, dict):
            return default
        for key in keys:
            if key in metadata:
                return metadata[key]
        return default

    @staticmethod
    def update_metadata_value(metadata, old_value, new_value) -> Dict[str, Any]:
        """Keep metadata key fields aligned when a node value is modified."""
        if not isinstance(metadata, dict):
            return {}
        updated = deepcopy(metadata)
        for key in ("valor", "value", "codigo", "id", "key"):
            if key in updated and updated[key] == old_value:
                updated[key] = new_value
        return updated

    # ── JSON export ───────────────────────────────────────────────────────────

    @staticmethod
    def compute_balance_factor(tree, node) -> int:
        """Compute balance factor for a node (left height - right height)."""
        left_height = (
            tree.getHeightNode(node.getLeftChild())
            if node.getLeftChild() is not None
            else -1
        )
        right_height = (
            tree.getHeightNode(node.getRightChild())
            if node.getRightChild() is not None
            else -1
        )
        return left_height - right_height

    @staticmethod
    def serialize_node_for_export(node, tree) -> Optional[Dict[str, Any]]:
        """Serialize a node with all business fields for JSON export."""
        if node is None:
            return None
        metadata = node.getMetadata() if hasattr(node, "getMetadata") else {}
        get = TreeSerializer.get_metadata_value
        promotions = get(metadata, ("promociones", "promotions"), []) or []
        alerts = get(metadata, ("alertas", "alerts"), []) or []
        return {
            "value": node.getValue(),
            "height": tree.getHeightNode(node),
            "balance_factor": TreeSerializer.compute_balance_factor(tree, node),
            "base_price": get(metadata, ("precio_base", "base_price", "precioBase")),
            "final_price": get(
                metadata, ("precio_final", "final_price", "precioFinal")
            ),
            "passengers": get(metadata, ("pasajeros", "passengers"), 0),
            "promotions": promotions,
            "alerts": alerts,
            "priority": get(metadata, ("prioridad", "priority"), "normal"),
            "metadata": deepcopy(metadata),
            "left": TreeSerializer.serialize_node_for_export(node.getLeftChild(), tree),
            "right": TreeSerializer.serialize_node_for_export(
                node.getRightChild(), tree
            ),
        }

    @staticmethod
    def compute_tree_summary(tree) -> Dict[str, Any]:
        """Build summary metrics (root, depth, nodes, leaves) for a tree."""
        properties = TreeLoadService.compute_tree_properties(tree)
        return {
            "root": properties["root"],
            "depth": properties["depth"],
            "nodes": properties["nodes"],
            "leaves": properties["leaves"],
        }
