"""Factory responsible for building and merging flight node metadata.

Single Responsibility: this class only knows how to construct and validate
the metadata dictionary for a flight node. It has no knowledge of trees,
HTTP, or serialization.

Open/Closed: new flight fields can be added by extending DEFAULTS without
modifying any endpoint code.
"""

from __future__ import annotations
from typing import Any, Dict


class FlightFactory:
    """Builds and merges flight metadata from raw request data."""

    # All known flight fields with their default values.
    # Add new fields here without touching any endpoint.
    DEFAULTS: Dict[str, Any] = {
        "origen": "",
        "destino": "",
        "horaSalida": "",
        "precioBase": 0,
        "precioFinal": 0,
        "pasajeros": 0,
        "prioridad": 1,
        "promocion": False,
        "alerta": False,
    }

    @staticmethod
    def build(data: Dict[str, Any], valor: Any) -> Dict[str, Any]:
        """Build a complete metadata dict from raw request data.

        Args:
            data: Raw dict from the HTTP request body.
            valor: The ordering key for the node (used as fallback for codigo).

        Returns:
            A full metadata dict with all flight fields populated.
        """
        metadata: Dict[str, Any] = {}
        metadata["codigo"] = data.get("codigo", valor)

        for field, default in FlightFactory.DEFAULTS.items():
            value = data.get(field, default)
            metadata[field] = default if value is None else value

        # Ensure precioFinal defaults to precioBase only when it was omitted.
        if "precioFinal" not in data or data.get("precioFinal") is None:
            metadata["precioFinal"] = metadata["precioBase"]

        return metadata

    @staticmethod
    def merge(existing: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merge update fields into existing metadata, preserving untouched fields.

        Args:
            existing: The node's current metadata dict.
            updates: Fields to update from the HTTP request body.

        Returns:
            A new metadata dict with updates applied over existing values.
        """
        merged = dict(existing)
        for field in ("codigo", *FlightFactory.DEFAULTS.keys()):
            if field in updates and updates[field] is not None:
                merged[field] = updates[field]

        # Keep precioFinal consistent after a precioBase update.
        if "precioBase" in updates and "precioFinal" not in updates:
            merged["precioFinal"] = updates["precioBase"]

        return merged
