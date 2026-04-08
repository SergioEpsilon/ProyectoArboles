"""
depth_routes.py
---------------
Flask Blueprint that exposes the Critical Depth Penalty API.

Endpoints
---------
GET  /depth-limit/get   → {"critical_depth": int | null}
POST /depth-limit/set   → set threshold and immediately re-apply penalties
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request, current_app

from services.depth_penalty_service import DepthPenaltyService
from services.tree_serializer import TreeSerializer

depth_bp = Blueprint("depth", __name__, url_prefix="/depth-limit")


# ---------------------------------------------------------------------------
# Helpers (mirrors the pattern used in stress_routes.py)
# ---------------------------------------------------------------------------


def _get_avl():
    """Return the current AVL instance via the late-binding getter in app.config."""
    return current_app.config["get_avl"]()


def _tree_snapshot(avl):
    """Serialise the AVL tree using the same method as the rest of app.py."""
    return TreeSerializer.to_dict(avl.root, avl)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@depth_bp.route("/get", methods=["GET"])
def get_depth_limit():
    """Return the current critical depth threshold."""
    return jsonify(DepthPenaltyService.instance().status()), 200


@depth_bp.route("/set", methods=["POST"])
def set_depth_limit():
    """
    Update the critical depth threshold and immediately recalculate
    all node prices and is_critical flags in the AVL tree.

    Body
    ----
    { "depth": <non-negative integer> }

    Response
    --------
    {
      "critical_depth": 3,
      "arbol": { ...serialised tree with updated is_critical / precioFinal... }
    }
    """
    data = request.get_json(silent=True) or {}
    depth = data.get("depth")

    if depth is None:
        return jsonify({"error": "El campo 'depth' es requerido."}), 400

    try:
        depth = int(depth)
    except (TypeError, ValueError):
        return jsonify({"error": "'depth' debe ser un número entero."}), 400

    try:
        svc = DepthPenaltyService.instance()
        svc.set_critical_depth(depth)

        avl = _get_avl()
        svc.apply_penalties(avl.root)

        return (
            jsonify(
                {
                    "message": f"Profundidad crítica establecida en {depth}. Precios recalculados.",
                    **svc.status(),
                    "arbol": _tree_snapshot(avl),
                }
            ),
            200,
        )

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422
