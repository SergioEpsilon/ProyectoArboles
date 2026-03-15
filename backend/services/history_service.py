"""Service responsible for the undo history stack (Ctrl+Z behavior)."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class HistoryService:
    """Manages a bounded LIFO stack of tree state snapshots for undo support.

    Follows the Single Responsibility Principle: this class only handles
    push/pop of action history. It does not know how snapshots are created
    or how trees are restored — those concerns belong to the caller.
    """

    def __init__(self, max_size: int = 50) -> None:
        self._stack: list[Dict[str, Any]] = []
        self._max_size = max_size

    def push(self, action_name: str, state: Dict[str, Any]) -> None:
        """Save a state snapshot before a mutation so it can be undone.

        Args:
            action_name: Label describing the action (e.g. 'insert-avl').
            state: Full tree snapshot produced by TreeSerializer.snapshot_state().
        """
        self._stack.append({"action": action_name, "state": state})
        # Enforce bounded size by discarding the oldest entry.
        if len(self._stack) > self._max_size:
            self._stack.pop(0)

    def pop(self) -> Dict[str, Any]:
        """Remove and return the most recent snapshot record.

        Returns:
            Dict with 'action' and 'state' keys.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._stack:
            raise IndexError("History stack is empty — nothing to undo.")
        return self._stack.pop()

    def is_empty(self) -> bool:
        """Return True if there are no actions to undo."""
        return len(self._stack) == 0

    def size(self) -> int:
        """Return the current number of entries in the history stack."""
        return len(self._stack)
