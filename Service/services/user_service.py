from functools import wraps

from flask import Blueprint, jsonify, request, g
from models.models import db, User

user_bp = Blueprint("user", __name__)

# ── Basic Auth helper ─────────────────────────────────────────────────────────

def require_auth(f):
    """Decorator: validates HTTP Basic Auth credentials against the DB."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return jsonify({"message": "Wymagana autoryzacja (Basic Auth)."}), 401
        user = User.query.filter_by(username=auth.username).first()
        if not user or user.password != auth.password:
            return jsonify({"message": "Nieprawidłowe dane logowania."}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


# ── Endpoints ─────────────────────────────────────────────────────────────────

@user_bp.route("/register", methods=["POST"])
def register_user():
    """POST /users/register  –  rejestracja nowego użytkownika."""
    try:
        body = request.json or {}
        username = body["username"]
        password = body["password"]

        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Istnieje już użytkownik o tym username."}), 400

        db.session.add(User(username=username, password=password))
        db.session.commit()
        return jsonify({
            "message": "Użytkownik dodany pomyślnie!",
            "_links": {
                "login_check": {"href": "/users/me", "method": "GET"},
                "flights":     {"href": "/flights",  "method": "GET"},
            }
        }), 201

    except KeyError as e:
        return jsonify({"message": f"Brak wymaganego pola: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@user_bp.route("/me", methods=["GET"])
@require_auth
def get_me():
    """GET /users/me  –  zwraca dane zalogowanego użytkownika."""
    u = g.current_user
    return jsonify({
        "id": u.id,
        "username": u.username,
        "_links": {
            "flights":      {"href": "/flights",      "method": "GET"},
            "reservations": {"href": "/reservations", "method": "GET"},
        }
    })
