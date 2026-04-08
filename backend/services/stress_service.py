"""
stress_service.py
-----------------
Manages the Stress Mode flag for the AVL tree.

Responsibilities (Single Responsibility):
    - Hold the stress_mode boolean state.
    - Expose enable / disable / query methods.
    - Does NOT hold a tree reference (no circular imports).
"""

from __future__ import annotations


class StressService:
    """
    Singleton service that controls whether AVL auto-balancing is active.

    Usage
    -----
    StressService.instance().enable()
    StressService.instance().is_active()   # True
    StressService.instance().disable()
    """

    _instance: StressService | None = None

    # ------------------------------------------------------------------
    # Singleton access
    # ------------------------------------------------------------------

    @classmethod
    def instance(cls) -> StressService:
        """Return the single shared instance, creating it on first call."""
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._stress_mode = False
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enable(self) -> None:
        """Activate stress mode: AVL will skip automatic rebalancing."""
        self._stress_mode = True

    def disable(self) -> None:
        """
        Deactivate stress mode.
        NOTE: does NOT rebalance the tree automatically —
        call AVL.rebalance_full() explicitly after this if needed.
        """
        self._stress_mode = False

    def is_active(self) -> bool:
        """Return True while stress mode is on."""
        return self._stress_mode

    def status(self) -> dict:
        """Return a serialisable status dict for API responses."""
        return {"stress_mode": self._stress_mode}
