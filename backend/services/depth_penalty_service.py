"""
depth_penalty_service.py
------------------------
Manages the critical depth limit and applies price penalties to tree nodes.

Single Responsibility:
  - Store the user-defined critical depth threshold.
  - Traverse the tree and mark nodes as critical / non-critical.
  - Recalculate precioFinal based on the 25% penalty rule.

Open/Closed:
  - The penalty multiplier (PENALTY_FACTOR) and the price keys are constants;
    new rules can be added without modifying existing methods.

This service mutates node metadata in-place so that TreeSerializer.to_dict()
picks up is_critical and precioFinal automatically through the existing
'data' field — no changes to TreeSerializer are needed.
"""

from __future__ import annotations

from typing import Optional


class DepthPenaltyService:
    """
    Singleton service that controls the critical depth limit and applies
    price penalties to nodes whose depth exceeds that limit.

    Usage
    -----
    DepthPenaltyService.instance().set_critical_depth(3)
    DepthPenaltyService.instance().apply_penalties(avl_tree.root)
    """

    PENALTY_FACTOR: float = 1.25  # +25 % on precioBase when node is critical

    _instance: Optional[DepthPenaltyService] = None

    # ------------------------------------------------------------------
    # Singleton access
    # ------------------------------------------------------------------

    @classmethod
    def instance(cls) -> DepthPenaltyService:
        """Return the single shared instance, creating it on first call."""
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._critical_depth = None
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_critical_depth(self, depth: int) -> None:
        """
        Set (or update) the critical depth threshold.
        Callers must call apply_penalties() after this to recalculate prices.
        """
        if not isinstance(depth, int) or depth < 0:
            raise ValueError(
                f"critical_depth must be a non-negative integer, got {depth!r}"
            )
        self._critical_depth = depth

    def get_critical_depth(self) -> Optional[int]:
        """Return the current threshold, or None if not yet configured."""
        return self._critical_depth

    def apply_penalties(self, root) -> None:
        """
        Traverse the entire tree starting at *root* and update each node's
        metadata in-place:

          - depth > critical_depth  →  is_critical = True,
                                       precioFinal = precioBase * PENALTY_FACTOR
          - otherwise               →  is_critical = False,
                                       precioFinal = precioBase  (reset)

        If critical_depth has not been set yet, the method is a no-op so
        trees without a configured limit are unaffected.
        """
        if self._critical_depth is None:
            return
        self._traverse(root, current_depth=0)

    def status(self) -> dict:
        """Return a serialisable status dict for API responses."""
        return {"critical_depth": self._critical_depth}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _traverse(self, node, current_depth: int) -> None:
        """
        Pre-order recursive traversal.
        Depth 0 = root, depth 1 = root's children, etc.
        """
        if node is None:
            return

        self._update_node(node, current_depth)

        self._traverse(node.getLeftChild(), current_depth + 1)
        self._traverse(node.getRightChild(), current_depth + 1)

    def _update_node(self, node, depth: int) -> None:
        """
        Read precioBase from metadata, apply or remove the penalty,
        and write is_critical back.  Both keys match FlightFactory.DEFAULTS.
        """
        metadata = node.getMetadata() if hasattr(node, "getMetadata") else {}

        precio_base: float = float(metadata.get("precioBase", 0) or 0)
        is_critical: bool = depth > self._critical_depth

        metadata["is_critical"] = is_critical
        metadata["precioFinal"] = (
            round(precio_base * self.PENALTY_FACTOR, 2) if is_critical else precio_base
        )

        # Persist the changes back into the node.
        if hasattr(node, "setMetadata"):
            node.setMetadata(metadata)
