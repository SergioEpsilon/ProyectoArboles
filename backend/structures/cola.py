"""Queue data structure used for pending insertion simulations."""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, List, Optional


class Queue:
	"""Simple FIFO queue with utility helpers for API serialization."""

	def __init__(self) -> None:
		self._items: Deque[Dict[str, Any]] = deque()

	def enqueue(self, item: Dict[str, Any]) -> None:
		"""Append one item at the end of the queue."""
		self._items.append(item)

	def dequeue(self) -> Optional[Dict[str, Any]]:
		"""Remove and return the oldest item, or None when empty."""
		if not self._items:
			return None
		return self._items.popleft()

	def peek(self) -> Optional[Dict[str, Any]]:
		"""Return the oldest item without removing it."""
		if not self._items:
			return None
		return self._items[0]

	def is_empty(self) -> bool:
		"""Return True when queue contains no items."""
		return len(self._items) == 0

	def size(self) -> int:
		"""Return current queue length."""
		return len(self._items)

	def clear(self) -> None:
		"""Remove all pending items from queue."""
		self._items.clear()

	def to_list(self) -> List[Dict[str, Any]]:
		"""Return a serializable list copy of all queued items."""
		return list(self._items)
