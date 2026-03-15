"""API endpoints for Legacy AI.

Add additional Blueprints or routes here.
"""

from flask import Blueprint

api_bp = Blueprint("api", __name__)


@api_bp.route("/healthz")
def healthz():
    """Health check endpoint."""
    return {"status": "ok"}
