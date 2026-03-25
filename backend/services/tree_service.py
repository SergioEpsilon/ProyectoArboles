"""Services for loading trees from user-provided JSON files."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from models.avl import AVL
from models.bst import BST
from models.node import Node


class TreeLoadService:
    """Encapsulates JSON parsing, tree reconstruction, and property extraction."""

    # Candidate keys that may contain the ordering value in JSON records.
    KEY_CANDIDATES = ("valor", "value", "codigo", "id", "key")
    # Candidate keys for left children in topology JSON mode.
    LEFT_KEYS = ("izquierdo", "left", "izq", "leftChild")
    # Candidate keys for right children in topology JSON mode.
    RIGHT_KEYS = ("derecho", "right", "der", "rightChild")

    @classmethod
    def _build_trees_from_roots(
        cls,
        avl_root_data: Any,
        bst_root_data: Any,
        key_field: Optional[str],
    ) -> Tuple[AVL, BST]:
        """Build AVL and BST instances from topology root payloads."""
        avl_tree = AVL()
        bst_tree = BST()
        avl_tree.root = (
            cls._build_node_from_topology(avl_root_data, key_field)
            if avl_root_data is not None
            else None
        )
        bst_tree.root = (
            cls._build_node_from_topology(bst_root_data, key_field)
            if bst_root_data is not None
            else None
        )
        return avl_tree, bst_tree

    @classmethod
    def load_both_trees(
        cls,
        json_data: Any,
        load_mode: Optional[str] = None,
        key_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Load AVL and BST from JSON using topology or insertion mode.

        This method is the main entry point used by Flask endpoints.
        """
        # Detect and unwrap SkyBalance export format automatically.
        if isinstance(json_data, dict) and "trees" in json_data:
            trees = json_data["trees"]
            if isinstance(trees, dict) and "AVL" in trees:
                avl_root = trees["AVL"].get("root")
                bst_root = trees.get("BST", {}).get("root")
                avl_tree, bst_tree = cls._build_trees_from_roots(
                    avl_root, bst_root, "value"
                )
                avl_props = cls.compute_tree_properties(avl_tree)
                bst_props = cls.compute_tree_properties(bst_tree)
                return {
                    "avl": avl_tree,
                    "bst": bst_tree,
                    "load_mode": "topology",
                    "detected_key": "value",
                    "properties": {"avl": avl_props, "bst": bst_props},
                }

        # Detect the load mode when client did not send an explicit one.
        detected_mode = cls.detect_load_mode(json_data, load_mode)
        # Detect the ordering key field from JSON structure when needed.
        detected_key = cls.detect_key_field(json_data, key_field)

        # Build both trees according to the selected mode.
        if detected_mode == "topology":
            avl_tree, bst_tree = cls._load_topology_mode(json_data, detected_key)
        else:
            avl_tree, bst_tree = cls._load_insertion_mode(json_data, detected_key)

        # Compute comparison properties requested by the requirement.
        avl_props = cls.compute_tree_properties(avl_tree)
        bst_props = cls.compute_tree_properties(bst_tree)

        # Return trees and diagnostics in a single response object.
        return {
            "avl": avl_tree,
            "bst": bst_tree,
            "load_mode": detected_mode,
            "detected_key": detected_key,
            "properties": {
                "avl": avl_props,
                "bst": bst_props,
            },
        }

    @classmethod
    def detect_load_mode(cls, json_data: Any, requested_mode: Optional[str]) -> str:
        """Detect load mode from request value or JSON shape."""
        # Respect explicit mode when it is valid.
        if isinstance(requested_mode, str):
            mode = requested_mode.strip().lower()
            if mode in {"topology", "insertion"}:
                return mode

        # Detect insertion mode from common wrapper fields.
        if isinstance(json_data, dict):
            data_type = str(json_data.get("tipo", "")).strip().lower()
            if data_type in {"insercion", "insertion"}:
                return "insertion"
            if isinstance(json_data.get("vuelos"), list):
                return "insertion"

        # Detect insertion mode when root is a list of items.
        if isinstance(json_data, list):
            return "insertion"

        # Default fallback is topology mode for nested object roots.
        return "topology"

    @classmethod
    def detect_key_field(
        cls, json_data: Any, requested_key: Optional[str]
    ) -> Optional[str]:
        """Detect which JSON field contains the sortable value."""
        # Respect explicit key when provided by the client.
        if isinstance(requested_key, str) and requested_key.strip():
            return requested_key.strip()

        # Try to infer from insertion wrapper list.
        if isinstance(json_data, dict) and isinstance(json_data.get("vuelos"), list):
            return cls._detect_key_from_items(json_data["vuelos"])

        # Try to infer from generic list payload.
        if isinstance(json_data, list):
            return cls._detect_key_from_items(json_data)

        # Try to infer directly from topology root object.
        if isinstance(json_data, dict):
            for key in cls.KEY_CANDIDATES:
                if key in json_data:
                    return key

        # Return None to indicate primitive values will be used directly.
        return None

    @classmethod
    def _detect_key_from_items(cls, items: List[Any]) -> Optional[str]:
        """Infer an ordering key from the first dictionary-like item."""
        # Scan items until a dictionary is found.
        for item in items:
            if isinstance(item, dict):
                for key in cls.KEY_CANDIDATES:
                    if key in item:
                        return key
                # If dictionary exists but no candidate key is found, fail early.
                raise ValueError(
                    "Could not detect ordering key in insertion list. "
                    "Provide 'key_field' or include one of: valor, value, codigo, id, key."
                )
        # When all items are primitive values, no key field is required.
        return None

    @classmethod
    def _load_topology_mode(
        cls, json_data: Any, key_field: Optional[str]
    ) -> Tuple[AVL, BST]:
        """Build AVL and BST by respecting parent/child topology from JSON."""
        # Topology mode requires object-like root or primitive root value.
        if json_data is None:
            raise ValueError("Topology mode received empty JSON content.")

        # Create both trees and attach reconstructed roots independently.
        return cls._build_trees_from_roots(json_data, json_data, key_field)

    @classmethod
    def _load_insertion_mode(
        cls, json_data: Any, key_field: Optional[str]
    ) -> Tuple[AVL, BST]:
        """Build AVL and BST by inserting values sequentially from JSON list."""
        # Normalize different insertion JSON shapes into one list.
        items = cls._extract_insertion_items(json_data)
        if len(items) == 0:
            raise ValueError("Insertion mode requires at least one item.")

        # Initialize target trees for parallel insertion.
        avl_tree = AVL()
        bst_tree = BST()
        expected_kind = None

        # Insert each parsed value into both trees in the same order.
        for item in items:
            value, metadata = cls._extract_value_and_metadata(item, key_field)
            cls._ensure_comparable_value(value)

            # Validate value-kind consistency to avoid runtime compare TypeError.
            value_kind = cls._kind_for_comparison(value)
            if expected_kind is None:
                expected_kind = value_kind
            elif expected_kind != value_kind:
                raise ValueError(
                    "Insertion list contains mixed non-comparable value kinds "
                    f"({expected_kind} and {value_kind})."
                )

            # Create separate nodes so each tree has independent objects.
            avl_tree.insert(Node(value, deepcopy(metadata)))
            bst_tree.insert(Node(value, deepcopy(metadata)))

        return avl_tree, bst_tree

    @classmethod
    def _extract_insertion_items(cls, json_data: Any) -> List[Any]:
        """Return insertion list from known JSON wrappers or direct list payload."""
        # Handle the common wrapper format: { "vuelos": [...] }.
        if isinstance(json_data, dict):
            for key in ("vuelos", "nodes", "items"):
                if isinstance(json_data.get(key), list):
                    return json_data[key]

        # Handle direct list payload sent by frontend.
        if isinstance(json_data, list):
            return json_data

        # Reject unsupported structures for insertion mode.
        raise ValueError("Insertion mode expects a list payload (vuelos/nodes/items).")

    @classmethod
    def _build_node_from_topology(
        cls, node_data: Any, key_field: Optional[str]
    ) -> Optional[Node]:
        """Recursively rebuild a tree node while preserving JSON topology."""
        # Preserve explicit null children from JSON topology.
        if node_data is None:
            return None

        # Extract value and metadata from current node payload.
        value, metadata = cls._extract_value_and_metadata(node_data, key_field)
        cls._ensure_comparable_value(value)

        # Instantiate current node with sortable value and original payload.
        node = Node(value, deepcopy(metadata))

        # Resolve child keys from Spanish/English variants.
        left_key = cls._find_existing_key(node_data, cls.LEFT_KEYS)
        right_key = cls._find_existing_key(node_data, cls.RIGHT_KEYS)

        # Build left subtree recursively and wire parent reference.
        if left_key is not None:
            left_child = cls._build_node_from_topology(
                node_data.get(left_key), key_field
            )
            node.setLeftChild(left_child)
            if left_child is not None:
                left_child.setParent(node)

        # Build right subtree recursively and wire parent reference.
        if right_key is not None:
            right_child = cls._build_node_from_topology(
                node_data.get(right_key), key_field
            )
            node.setRightChild(right_child)
            if right_child is not None:
                right_child.setParent(node)

        return node

    @classmethod
    def _extract_value_and_metadata(
        cls,
        item: Any,
        key_field: Optional[str],
    ) -> Tuple[Any, Dict[str, Any]]:
        """Extract comparable value and preserve full metadata payload."""
        # Primitive payload is considered directly as tree value.
        if not isinstance(item, dict):
            return item, {"raw": item}

        # Use explicit/detected key when available.
        if key_field is not None and key_field in item:
            return item[key_field], dict(item)

        # Attempt best-effort detection when key_field was not provided.
        for candidate in cls.KEY_CANDIDATES:
            if candidate in item:
                return item[candidate], dict(item)

        # Reject dictionaries that do not expose any sortable key.
        raise ValueError(
            "Could not extract sortable value from JSON node. "
            "Include one of: valor, value, codigo, id, key."
        )

    @classmethod
    def _find_existing_key(
        cls, payload: Any, candidates: Tuple[str, ...]
    ) -> Optional[str]:
        """Return the first matching key from candidate names."""
        # Non-dictionary payload cannot contain child keys.
        if not isinstance(payload, dict):
            return None

        # Return first key found to support flexible JSON vocabulary.
        for key in candidates:
            if key in payload:
                return key
        return None

    @staticmethod
    def _ensure_comparable_value(value: Any) -> None:
        """Validate that tree values are simple comparable scalar types."""
        # Accept standard scalar types used in ordering comparisons.
        if isinstance(value, (int, float, str)):
            return

        # Explicitly reject unsupported ordering types.
        raise ValueError(
            "Sortable node values must be int, float, or str. "
            f"Received type: {type(value).__name__}."
        )

    @staticmethod
    def _kind_for_comparison(value: Any) -> str:
        """Return normalized comparison kind for insertion consistency checks."""
        # Group integers and floats under numeric family.
        if isinstance(value, (int, float)):
            return "number"
        # Strings belong to textual ordering family.
        if isinstance(value, str):
            return "string"
        # Unknown kind is handled by _ensure_comparable_value before this point.
        return "unknown"

    @classmethod
    def compute_tree_properties(cls, tree: Any) -> Dict[str, Any]:
        """Compute root, depth, leaves, and node count for a tree instance."""
        # Handle empty trees consistently.
        if tree is None or tree.root is None:
            return {
                "root": None,
                "depth": 0,
                "leaves": 0,
                "nodes": 0,
            }

        # Use model height helper as depth metric (root depth of leaf = 0).
        depth = tree.getHeightNode(tree.root)

        # Traverse once to compute global counts.
        nodes, leaves = cls._count_nodes_and_leaves(tree.root)

        return {
            "root": tree.root.getValue(),
            "depth": depth,
            "leaves": leaves,
            "nodes": nodes,
        }

    @classmethod
    def _count_nodes_and_leaves(cls, node: Optional[Node]) -> Tuple[int, int]:
        """Count total nodes and leaves in a single recursive traversal."""
        if node is None:
            return 0, 0

        left_nodes, left_leaves = cls._count_nodes_and_leaves(node.getLeftChild())
        right_nodes, right_leaves = cls._count_nodes_and_leaves(node.getRightChild())

        is_leaf = node.getLeftChild() is None and node.getRightChild() is None
        total_nodes = 1 + left_nodes + right_nodes
        total_leaves = (1 if is_leaf else 0) + left_leaves + right_leaves
        return total_nodes, total_leaves
