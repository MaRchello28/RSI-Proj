import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    reservations = db.relationship("Reservation", backref="user", lazy=True)


class Flight(db.Model):
    __tablename__ = "flights"

    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), unique=True, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.String(50), nullable=False)  # ISO format string
    arrival_time = db.Column(db.String(50), nullable=False)
    seats_total = db.Column(db.Integer, nullable=False, default=100)
    seats_available = db.Column(db.Integer, nullable=False, default=100)
    price = db.Column(db.Float, nullable=False, default=0.0)

    reservations = db.relationship("Reservation", backref="flight", lazy=True)

    def to_dict(self, include_links=True):
        data = {
            "id": self.id,
            "flight_number": self.flight_number,
            "origin": self.origin,
            "destination": self.destination,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "seats_available": self.seats_available,
            "price": self.price,
        }
        if include_links:
            data["_links"] = {
                "self": {"href": f"/flights/{self.id}", "method": "GET"},
                "book": {"href": f"/reservations", "method": "POST"},
                "all_flights": {"href": "/flights", "method": "GET"},
            }
        return data


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    reservation_number = db.Column(db.String(36), unique=True, nullable=False,
                                   default=lambda: str(uuid.uuid4()).upper()[:8])
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey("flights.id"), nullable=False)
    passenger_name = db.Column(db.String(200), nullable=False)
    passenger_email = db.Column(db.String(200), nullable=False)
    seats = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="confirmed")

    def to_dict(self, include_links=True):
        data = {
            "id": self.id,
            "reservation_number": self.reservation_number,
            "passenger_name": self.passenger_name,
            "passenger_email": self.passenger_email,
            "seats": self.seats,
            "total_price": self.total_price,
            "created_at": self.created_at,
            "status": self.status,
            "flight": self.flight.to_dict(include_links=False) if self.flight else None,
        }
        if include_links:
            data["_links"] = {
                "self": {"href": f"/reservations/{self.reservation_number}", "method": "GET"},
                "ticket_pdf": {"href": f"/reservations/{self.reservation_number}/ticket", "method": "GET"},
                "cancel": {"href": f"/reservations/{self.reservation_number}", "method": "DELETE"},
                "all_reservations": {"href": "/reservations", "method": "GET"},
            }
        return data
