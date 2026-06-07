from flask import Blueprint, jsonify, request
from models.models import db, Flight

flight_bp = Blueprint("flight", __name__)


@flight_bp.route("/", methods=["GET"])
def list_flights():
    """
    GET /flights/
    Query params: origin, destination, date (YYYY-MM-DD)
    Returns all (optionally filtered) flights.
    """
    origin      = request.args.get("origin", "").strip()
    destination = request.args.get("destination", "").strip()
    date        = request.args.get("date", "").strip()

    query = Flight.query

    if origin:
        query = query.filter(Flight.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(Flight.destination.ilike(f"%{destination}%"))
    if date:
        query = query.filter(Flight.departure_time.like(f"{date}%"))

    flights = query.all()
    return jsonify({
        "count": len(flights),
        "flights": [f.to_dict() for f in flights],
        "_links": {
            "self":   {"href": "/flights/",    "method": "GET"},
            "search": {"href": "/flights/?origin=&destination=&date=", "method": "GET"},
            "book":   {"href": "/reservations", "method": "POST"},
        }
    })


@flight_bp.route("/<int:flight_id>", methods=["GET"])
def get_flight(flight_id):
    """GET /flights/<id>  –  szczegóły konkretnego lotu."""
    flight = Flight.query.get_or_404(flight_id, description="Lot nie istnieje.")
    return jsonify(flight.to_dict())


# ── Admin: add flight ─────────────────────────────────────────────────────────

@flight_bp.route("/", methods=["POST"])
def add_flight():
    """POST /flights/  –  dodaj nowy lot (admin / seed)."""
    try:
        body = request.json or {}
        flight = Flight(
            flight_number   = body["flight_number"],
            origin          = body["origin"],
            destination     = body["destination"],
            departure_time  = body["departure_time"],
            arrival_time    = body["arrival_time"],
            seats_total     = body.get("seats_total", 100),
            seats_available = body.get("seats_total", 100),
            price           = body.get("price", 0.0),
        )
        db.session.add(flight)
        db.session.commit()
        return jsonify(flight.to_dict()), 201
    except KeyError as e:
        return jsonify({"message": f"Brak wymaganego pola: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
