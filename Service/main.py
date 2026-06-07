from flask import Flask, jsonify
from flask_cors import CORS

from models.models import db, Flight
from services.user_service import user_bp
from services.flight_service import flight_bp
from services.reservation_service import reservation_bp
from filters.filters import register_filters
from filters.error_handlers import register_error_handlers

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_AS_ASCII"] = False  # proper UTF-8 in responses

db.init_app(app)

# ── Filters & error handlers ──────────────────────────────────────────────────
register_filters(app)
register_error_handlers(app)

# ── Blueprints ────────────────────────────────────────────────────────────────
app.register_blueprint(user_bp,        url_prefix="/users")
app.register_blueprint(flight_bp,      url_prefix="/flights")
app.register_blueprint(reservation_bp, url_prefix="/reservations")

# ── DB init + seed data ───────────────────────────────────────────────────────
with app.app_context():
    db.create_all()

    # Seed example flights if table is empty
    if Flight.query.count() == 0:
        sample_flights = [
            Flight(flight_number="LOT101", origin="Warszawa", destination="Londyn",
                   departure_time="2025-08-01T08:00:00", arrival_time="2025-08-01T10:30:00",
                   seats_total=150, seats_available=150, price=299.99),
            Flight(flight_number="LOT202", origin="Warszawa", destination="Paryż",
                   departure_time="2025-08-01T11:00:00", arrival_time="2025-08-01T13:20:00",
                   seats_total=120, seats_available=120, price=249.00),
            Flight(flight_number="LOT303", origin="Kraków",   destination="Berlin",
                   departure_time="2025-08-02T07:30:00", arrival_time="2025-08-02T09:00:00",
                   seats_total=80,  seats_available=80,  price=179.50),
            Flight(flight_number="LOT404", origin="Gdańsk",   destination="Amsterdam",
                   departure_time="2025-08-03T06:00:00", arrival_time="2025-08-03T08:45:00",
                   seats_total=100, seats_available=100, price=319.00),
            Flight(flight_number="LOT505", origin="Warszawa", destination="Rzym",
                   departure_time="2025-08-05T14:00:00", arrival_time="2025-08-05T17:30:00",
                   seats_total=200, seats_available=200, price=389.00),
        ]
        db.session.bulk_save_objects(sample_flights)
        db.session.commit()
        print("✔ Dodano przykładowe loty do bazy danych.")


# ── Root endpoint (HATEOAS entry point) ───────────────────────────────────────
@app.route("/")
def index():
    return jsonify({
        "service": "Flight Booking API",
        "version": "1.0",
        "_links": {
            "flights":      {"href": "/flights/",      "method": "GET"},
            "search":       {"href": "/flights/?origin=&destination=&date=", "method": "GET"},
            "register":     {"href": "/users/register","method": "POST"},
            "my_profile":   {"href": "/users/me",      "method": "GET"},
            "reservations": {"href": "/reservations/", "method": "GET"},
        }
    })


if __name__ == "__main__":
    import threading

    def run_http():
        app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)

    def run_https():
        app.run(host="0.0.0.0", port=5443, debug=False, use_reloader=False, ssl_context=("cert.pem", "key.pem"))

    t1 = threading.Thread(target=run_http)
    t2 = threading.Thread(target=run_https)
    t1.start()
    t2.start()
    t1.join()
    t2.join()