import time
import logging
from functools import wraps
from flask import request, jsonify, g

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("flight_api")

# ── Simple in-memory Basic-Auth store (extend with DB as needed) ──────────────
_VALID_TOKENS: set[str] = set()   # populated at runtime via /users/register+login


def register_filters(app):
    """Attach before/after request hooks to the Flask app."""

    @app.before_request
    def log_request():
        g.start_time = time.time()
        logger.info("→ %s %s  body=%s", request.method, request.path,
                    request.get_data(as_text=True)[:200] or "<empty>")

    @app.after_request
    def log_response(response):
        elapsed = (time.time() - g.get("start_time", time.time())) * 1000
        logger.info("← %s %s  status=%s  %.1fms",
                    request.method, request.path, response.status_code, elapsed)
        # HATEOAS: always return JSON content-type for API responses
        return response

    @app.after_request
    def add_cors_headers(response):
        response.headers["X-Powered-By"] = "FlightAPI/1.0"
        return response
