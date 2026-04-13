"""
stress_routes.py
----------------
Flask Blueprint that exposes the Stress Mode API.

Endpoints
---------
GET  /stress/status      -> {"stress_mode": bool}
POST /stress/enable      -> activates stress mode
POST /stress/disable     -> deactivates stress mode (does NOT rebalance)
POST /stress/rebalance   -> forces global AVL rebalance and returns stats
"""

from __future__ import annotations

from flask import Blueprint, jsonify, current_app

from services.stress_service import StressService
from services.tree_serializer import TreeSerializer

from services.auditoria_avl import verificar_propiedad_avl

stress_bp = Blueprint("stress", __name__, url_prefix="/stress")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_avl():
    """
    Return the current AVL instance via the late-binding getter registered
    in app.config. This avoids circular imports and always reflects the
    latest instance even after _restore() or _rebalance() in app.py.
    """
    return current_app.config["get_avl"]()


def _tree_snapshot(avl):
    """Serialise the current AVL for the frontend using the same method as app.py."""
    return TreeSerializer.to_dict(avl.root, avl)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@stress_bp.route("/status", methods=["GET"])
def status():
    """Return whether stress mode is currently active."""
    return jsonify(StressService.instance().status()), 200


@stress_bp.route("/enable", methods=["POST"])
def enable():
    """
    Activate stress mode.
    From this point, AVL insertions / deletions will NOT auto-balance.
    """
    StressService.instance().enable()
    return (
        jsonify(
            {
                "message": "Modo estres activado. El balanceo automatico esta deshabilitado.",
                **StressService.instance().status(),
            }
        ),
        200,
    )


@stress_bp.route("/disable", methods=["POST"])
def disable():
    """
    Deactivate stress mode WITHOUT rebalancing.
    Call /stress/rebalance separately if you want the tree corrected.
    """
    StressService.instance().disable()
    return (
        jsonify(
            {
                "message": (
                    "Modo estres desactivado. "
                    "El arbol puede seguir desbalanceado — use /stress/rebalance para corregirlo."
                ),
                **StressService.instance().status(),
            }
        ),
        200,
    )


@stress_bp.route("/rebalance", methods=["POST"])
def rebalance():
    """
    Force a full AVL rebalance regardless of stress mode state.

    Response
    --------
    {
        "rotations": {"LL": 2, "RR": 1, "LR": 0, "RL": 0, "total": 3},
        "arbol": { ...serialised tree... }
    }
    """
    avl = _get_avl()
    if avl is None or avl.root is None:
        return (
            jsonify({"error": "El arbol esta vacio, no hay nada que rebalancear."}),
            400,
        )

    stats = avl.rebalance_full()

    return (
        jsonify(
            {
                "message": f"Rebalanceo global completado. {stats['total']} rotaciones aplicadas.",
                "rotations": stats,
                "arbol": _tree_snapshot(avl),
            }
        ),
        200,
    )

@stress_bp.route("/audit", methods=["GET"])
def audit():
    """
    Run AVL only if stress mode is active.
    """

    if not StressService.instance().is_active():
        return (
            jsonify({
                "error": "la auditoria AVL solo esta disponible en estres"
            }),
            403,
        )
    avl = _get_avl()
    if avl is None or avl.root is None:
        return (
            jsonify({"error": "El arbol esta vacio"}),
            400,
        )
    
    resultado = verificar_propiedad_avl(avl)

    return (
        jsonify({
            "message": "Auditoria AVL ejecutada correctamente",
            "resultado": resultado
        }),
        200,
    )

