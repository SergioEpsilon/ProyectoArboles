"""Service responsible for named version management of tree state."""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class VersionService:
    """Handles saving and restoring named snapshots of the tree state.

    Follows the Single Responsibility Principle: this class only manages
    named versions. History (undo stack) is handled separately.
    """

    def __init__(self) -> None:
        # Internal store: version name -> version record.
        self._store: Dict[str, Dict[str, Any]] = {}
        self._storage_file = self._default_storage_file()
        self._load_from_disk()

    @staticmethod
    def _default_storage_file() -> Path:
        """Return the JSON file used to persist user versions."""
        backend_dir = Path(__file__).resolve().parents[1]
        project_root = backend_dir.parent
        return project_root / "data" / "saved_versions.json"

    def _load_from_disk(self) -> None:
        """Load saved versions from disk, ignoring malformed payloads safely."""
        if not self._storage_file.exists():
            return

        try:
            with self._storage_file.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (json.JSONDecodeError, OSError):
            # Keep in-memory store empty if file cannot be parsed/read.
            return

        if not isinstance(payload, dict):
            return

        raw_versions = payload.get("versions", {})
        if not isinstance(raw_versions, dict):
            return

        sanitized: Dict[str, Dict[str, Any]] = {}
        for name, record in raw_versions.items():
            if not isinstance(name, str) or not isinstance(record, dict):
                continue

            saved_at = record.get("saved_at")
            state = record.get("state")
            if not isinstance(saved_at, str) or not isinstance(state, dict):
                continue

            sanitized[name] = {
                "name": name,
                "saved_at": saved_at,
                "state": state,
            }

        self._store = sanitized

    def _persist_to_disk(self) -> None:
        """Write all saved versions to disk in a stable JSON structure."""
        self._storage_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "versions": self._store,
        }
        with self._storage_file.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def save(self, name: str, state: Dict[str, Any]) -> None:
        """Save a named version with the given tree state snapshot.

        Args:
            name: Human-readable version label (e.g. 'Simulación Alta Demanda').
            state: Full tree snapshot produced by TreeSerializer.snapshot_state().
        """
        self._store[name] = {
            "name": name,
            "saved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "state": copy.deepcopy(state),
        }
        self._persist_to_disk()

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
        return copy.deepcopy(self._store[name]["state"])

    def list_versions(self) -> List[Dict[str, str]]:
        """Return a list of saved versions with name and timestamp.

        Returns:
            List of dicts with 'name' and 'saved_at' fields.
        """
        versions = [
            {"name": v["name"], "saved_at": v["saved_at"]} for v in self._store.values()
        ]
        return sorted(versions, key=lambda item: item["saved_at"], reverse=True)

    def exists(self, name: str) -> bool:
        """Check whether a version with the given name exists."""
        return name in self._store
