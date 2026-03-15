"""Service responsible for named version management of tree state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class VersionService:
    """Handles saving and restoring named snapshots of the tree state.

    Follows the Single Responsibility Principle: this class only manages
    named versions. History (undo stack) is handled separately.
    """

    def __init__(self) -> None:
        # Internal store: version name -> version record.
        self._store: Dict[str, Dict[str, Any]] = {}

    def save(self, name: str, state: Dict[str, Any]) -> None:
        """Save a named version with the given tree state snapshot.

        Args:
            name: Human-readable version label (e.g. 'Simulación Alta Demanda').
            state: Full tree snapshot produced by TreeSerializer.snapshot_state().
        """
        self._store[name] = {
            "name": name,
            "saved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "state": state,
        }

    def restore(self, name: str) -> Dict[str, Any]:
        """Return the state snapshot for the given version name.

        Args:
            name: Version label to restore.

        Returns:
            The stored state snapshot.

        Raises:
            KeyError: If no version with that name exists.
        """
        if name not in self._store:
            raise KeyError(f"Version '{name}' does not exist.")
        return self._store[name]["state"]

    def list_versions(self) -> List[Dict[str, str]]:
        """Return a list of saved versions with name and timestamp.

        Returns:
            List of dicts with 'name' and 'saved_at' fields.
        """
        return [
            {"name": v["name"], "saved_at": v["saved_at"]} for v in self._store.values()
        ]

    def exists(self, name: str) -> bool:
        """Check whether a version with the given name exists."""
        return name in self._store
