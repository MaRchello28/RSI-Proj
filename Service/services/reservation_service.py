import io
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request, send_file, g
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from models.models import db, Flight, Reservation
from services.user_service import require_auth

reservation_bp = Blueprint("reservation", __name__)


# ── Helper: generate PDF ticket ───────────────────────────────────────────────

def _generate_ticket_pdf(reservation: Reservation) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("title", parent=styles["Title"],
                                 fontSize=22, textColor=colors.HexColor("#1a3a5c"),
                                 spaceAfter=6, alignment=TA_CENTER)
    sub_style   = ParagraphStyle("sub", parent=styles["Normal"],
                                 fontSize=11, textColor=colors.grey,
                                 spaceAfter=4, alignment=TA_CENTER)
    label_style = ParagraphStyle("label", parent=styles["Normal"],
                                 fontSize=9, textColor=colors.grey)
    value_style = ParagraphStyle("value", parent=styles["Normal"],
                                 fontSize=12, textColor=colors.HexColor("#1a3a5c"),
                                 fontName="Helvetica-Bold")

    # Header
    story.append(Paragraph("✈  BOARDING PASS", title_style))
    story.append(Paragraph("Potwierdzenie rezerwacji", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 0.4*cm))

    flight = reservation.flight

    # Route row
    route_data = [
        [Paragraph(f"<b>{flight.origin}</b>", ParagraphStyle("r", fontSize=18, alignment=TA_CENTER)),
         Paragraph("→", ParagraphStyle("arr", fontSize=18, alignment=TA_CENTER)),
         Paragraph(f"<b>{flight.destination}</b>", ParagraphStyle("r", fontSize=18, alignment=TA_CENTER))],
    ]
    route_table = Table(route_data, colWidths=[6*cm, 3*cm, 6*cm])
    route_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(route_table)
    story.append(Spacer(1, 0.4*cm))

    # Details table
    details = [
        ["Numer lotu",       flight.flight_number,
         "Numer rezerwacji", reservation.reservation_number],
        ["Odlot",            flight.departure_time,
         "Przylot",          flight.arrival_time],
        ["Pasażer",          reservation.passenger_name,
         "E-mail",           reservation.passenger_email],
        ["Liczba miejsc",    str(reservation.seats),
         "Łączna cena",      f"{reservation.total_price:.2f} PLN"],
        ["Status",           reservation.status.upper(),
         "Data rezerwacji",  reservation.created_at[:19]],
    ]

    col_w = [3.5*cm, 5*cm, 3.5*cm, 5*cm]
    det_table = Table(details, colWidths=col_w, repeatRows=0)
    det_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#eaf1fb")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#eaf1fb")),
        ("FONTNAME",   (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",   (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, colors.HexColor("#f5f9ff")]),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#c0d0e0")),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    story.append(det_table)
    story.append(Spacer(1, 0.6*cm))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c"), dash=(4,3)))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Dziękujemy za skorzystanie z naszych usług. Prosimy stawić się na lotnisku co najmniej 2 godziny przed odlotem.",
        ParagraphStyle("footer", parent=styles["Normal"], fontSize=9,
                       textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ── Endpoints ─────────────────────────────────────────────────────────────────

@reservation_bp.route("/", methods=["POST"])
@require_auth
def buy_ticket():
    """
    POST /reservations/
    Body: { flight_id, passenger_name, passenger_email, seats }
    Auth: Basic Auth
    Kupuje bilet i zwraca potwierdzenie z linkiem do PDF.
    """
    try:
        body = request.json or {}
        flight_id      = body["flight_id"]
        passenger_name = body["passenger_name"]
        passenger_email= body["passenger_email"]
        seats          = int(body.get("seats", 1))

        flight = Flight.query.get(flight_id)
        if not flight:
            return jsonify({"message": "Lot nie istnieje."}), 404
        if flight.seats_available < seats:
            return jsonify({"message": f"Niewystarczająca liczba miejsc. Dostępne: {flight.seats_available}"}), 400

        total = round(flight.price * seats, 2)
        res_number = str(uuid.uuid4()).upper()[:8]

        reservation = Reservation(
            reservation_number = res_number,
            user_id            = g.current_user.id,
            flight_id          = flight_id,
            passenger_name     = passenger_name,
            passenger_email    = passenger_email,
            seats              = seats,
            total_price        = total,
            created_at         = datetime.now().isoformat(timespec="seconds"),
            status             = "confirmed",
        )
        flight.seats_available -= seats
        db.session.add(reservation)
        db.session.commit()

        return jsonify({
            "message": "Rezerwacja zakończona sukcesem!",
            "reservation": reservation.to_dict(),
        }), 201

    except KeyError as e:
        return jsonify({"message": f"Brak wymaganego pola: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@reservation_bp.route("/", methods=["GET"])
@require_auth
def list_reservations():
    """GET /reservations/  –  lista rezerwacji zalogowanego użytkownika."""
    reservations = Reservation.query.filter_by(user_id=g.current_user.id).all()
    return jsonify({
        "count": len(reservations),
        "reservations": [r.to_dict() for r in reservations],
        "_links": {
            "self": {"href": "/reservations/", "method": "GET"},
            "buy":  {"href": "/reservations/", "method": "POST"},
        }
    })


@reservation_bp.route("/<string:reservation_number>", methods=["GET"])
def get_reservation(reservation_number):
    """
    GET /reservations/<number>
    Sprawdza rezerwację po numerze (bez autoryzacji – publiczny podgląd).
    """
    res = Reservation.query.filter_by(reservation_number=reservation_number.upper()).first()
    if not res:
        return jsonify({"message": "Rezerwacja nie istnieje."}), 404
    return jsonify(res.to_dict())


@reservation_bp.route("/<string:reservation_number>/ticket", methods=["GET"])
def get_ticket_pdf(reservation_number):
    """
    GET /reservations/<number>/ticket
    Pobiera bilet w formacie PDF.
    """
    res = Reservation.query.filter_by(reservation_number=reservation_number.upper()).first()
    if not res:
        return jsonify({"message": "Rezerwacja nie istnieje."}), 404

    pdf_buffer = _generate_ticket_pdf(res)
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"bilet_{res.reservation_number}.pdf",
    )


@reservation_bp.route("/<string:reservation_number>", methods=["DELETE"])
@require_auth
def cancel_reservation(reservation_number):
    """DELETE /reservations/<number>  –  anuluje rezerwację."""
    res = Reservation.query.filter_by(
        reservation_number=reservation_number.upper(),
        user_id=g.current_user.id
    ).first()
    if not res:
        return jsonify({"message": "Rezerwacja nie istnieje lub brak dostępu."}), 404
    if res.status == "cancelled":
        return jsonify({"message": "Rezerwacja już jest anulowana."}), 400

    res.status = "cancelled"
    res.flight.seats_available += res.seats
    db.session.commit()
    return jsonify({
        "message": "Rezerwacja anulowana.",
        "_links": {"flights": {"href": "/flights/", "method": "GET"}}
    })
