"""Service responsible for persistent storage of pending insertion requests.

Implements disk-backed queue that survives backend restarts.
Maintains separate queues for AVL and BST modes.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List

from structures.cola import Queue


class QueuePersistenceService:
    """Manages loading and saving pending insertion queues to disk.

    Follows single responsibility: only handles disk I/O for queue state.
    Does not perform tree operations or insertion logic.
    """

    def __init__(self, tree_modes: List[str] = None) -> None:
        """Initialize queue persistence service.

        Args:
            tree_modes: List of tree mode names to manage (default: ['AVL', 'BST']).
        """
        if tree_modes is None:
            tree_modes = ["AVL", "BST"]

        self._modes = tree_modes
        self._storage_file = self._default_storage_file()
        self._queues: Dict[str, Queue] = {modo: Queue() for modo in self._modes}
        self._load_from_disk()

    @staticmethod
    def _default_storage_file() -> Path:
        """Return the JSON file used to persist pending insertion queues."""
        backend_dir = Path(__file__).resolve().parents[1]
        project_root = backend_dir.parent
        return project_root / "data" / "pending_queue.json"

    def _load_from_disk(self) -> None:
        """Load all queues from disk, silently handling missing/malformed files."""
        if not self._storage_file.exists():
            return

        try:
            with self._storage_file.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return

        if not isinstance(payload, dict):
            return

        queues_data = payload.get("queues", {})
        if not isinstance(queues_data, dict):
            return

        for modo in self._modes:
            items = queues_data.get(modo, [])
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue
                # Validate required fields exist
                if "valor" in item and "metadata" in item:
                    self._queues[modo].enqueue(item)

    def _persist_to_disk(self) -> None:
        """Write all queue state to disk in stable JSON format."""
        self._storage_file.parent.mkdir(parents=True, exist_ok=True)

        queues_data = {}
        for modo in self._modes:
            queues_data[modo] = self._queues[modo].to_list()

        payload = {
            "saved_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "queues": queues_data,
        }

        with self._storage_file.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def get_queue(self, modo: str) -> Queue:
        """Return the queue for the given tree mode."""
        if modo not in self._queues:
            raise ValueError(f"Unknown tree mode: {modo}")
        return self._queues[modo]

    def enqueue(self, modo: str, item: Dict[str, Any]) -> None:
        """Add an item to the queue for the given mode and persist to disk."""
        self.get_queue(modo).enqueue(copy.deepcopy(item))
        self._persist_to_disk()

    def dequeue(self, modo: str) -> Any:
        """Remove and return oldest item from queue, then persist state."""
        queue = self.get_queue(modo)
        item = queue.dequeue()
        if item is not None:
            self._persist_to_disk()
        return item

    def clear_queue(self, modo: str) -> None:
        """Remove all items from a queue and persist to disk."""
        self.get_queue(modo).clear()
        self._persist_to_disk()

    def clear_all_queues(self) -> None:
        """Remove all items from all queues and persist to disk."""
        for queue in self._queues.values():
            queue.clear()
        self._persist_to_disk()

    def list_all_queues(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return serializable representation of all queues."""
        return {modo: self._queues[modo].to_list() for modo in self._modes}
