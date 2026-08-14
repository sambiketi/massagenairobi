from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from app import db
from app.models import Booking


api_bp = Blueprint('api', __name__)


# ============================================================
# CREATE BOOKING
# ============================================================

@api_bp.route('/book', methods=['POST'])
def create_booking():
    """
    Create a new massage booking.

    Required fields:
        name
        phone
        date
        time
        service
    """

    try:
        # ----------------------------------------------------
        # Validate JSON
        # ----------------------------------------------------
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid or missing JSON data'
            }), 400

        # ----------------------------------------------------
        # Required fields
        # ----------------------------------------------------
        required_fields = [
            'name',
            'phone',
            'date',
            'time',
            'service'
        ]

        missing = []

        for field in required_fields:
            value = data.get(field)

            if value is None or str(value).strip() == '':
                missing.append(field)

        if missing:
            return jsonify({
                'success': False,
                'error': 'Missing required fields',
                'missing': missing
            }), 400

        # ----------------------------------------------------
        # Clean input
        # ----------------------------------------------------
        name = str(data.get('name')).strip()
        phone = str(data.get('phone')).strip()
        service = str(data.get('service')).strip()
        date_value = str(data.get('date')).strip()
        time_value = str(data.get('time')).strip()

        # ----------------------------------------------------
        # Validate name
        # ----------------------------------------------------
        if len(name) < 2:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid name'
            }), 400

        # ----------------------------------------------------
        # Validate phone
        # ----------------------------------------------------
        if len(phone) < 7:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid phone number'
            }), 400

        # ----------------------------------------------------
        # Validate service
        # ----------------------------------------------------
        if len(service) < 2:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid service'
            }), 400

        # ----------------------------------------------------
        # Parse date
        # ----------------------------------------------------
        try:
            appointment_date = datetime.strptime(
                date_value,
                '%Y-%m-%d'
            ).date()

        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD.'
            }), 400

        # ----------------------------------------------------
        # Parse time
        # ----------------------------------------------------
        try:
            appointment_time = datetime.strptime(
                time_value,
                '%H:%M'
            ).time()

        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid time format. Use HH:MM.'
            }), 400

        # ----------------------------------------------------
        # Prevent bookings in the past
        # ----------------------------------------------------
        now = datetime.now()

        appointment_datetime = datetime.combine(
            appointment_date,
            appointment_time
        )

        if appointment_datetime < now:
            return jsonify({
                'success': False,
                'error': 'You cannot book a date or time in the past'
            }), 400

        # ----------------------------------------------------
        # Create booking
        # ----------------------------------------------------
        booking = Booking(
            client_name=name,
            client_phone=phone,
            service=service,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='Pending'
        )

        db.session.add(booking)
        db.session.commit()

        current_app.logger.info(
            f"BOOKING CREATED | "
            f"id={booking.id} | "
            f"name={name} | "
            f"phone={phone} | "
            f"service={service} | "
            f"date={appointment_date} | "
            f"time={appointment_time}"
        )

        return jsonify({
            'success': True,
            'message': 'Booking created successfully',
            'booking': booking.to_dict()
        }), 201

    except Exception as e:

        db.session.rollback()

        current_app.logger.exception(
            f"BOOKING CREATION FAILED: {str(e)}"
        )

        return jsonify({
            'success': False,
            'error': 'Unable to create booking',
            'debug': str(e) if current_app.debug else None
        }), 500


# ============================================================
# GET BOOKINGS
# ============================================================

@api_bp.route('/bookings', methods=['GET'])
def get_bookings():
    """
    Get bookings.

    Optional:
        ?status=Pending
    """

    try:

        status = request.args.get('status')

        query = Booking.query

        if status:
            query = query.filter_by(status=status)

        bookings = query.order_by(
            Booking.appointment_date.desc(),
            Booking.appointment_time.desc()
        ).all()

        return jsonify({
            'success': True,
            'count': len(bookings),
            'bookings': [
                booking.to_dict()
                for booking in bookings
            ]
        })

    except Exception as e:

        current_app.logger.exception(
            f"GET BOOKINGS FAILED: {str(e)}"
        )

        return jsonify({
            'success': False,
            'error': 'Unable to retrieve bookings'
        }), 500


# ============================================================
# GET SINGLE BOOKING
# ============================================================

@api_bp.route('/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):

    try:

        booking = Booking.query.get(booking_id)

        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404

        return jsonify({
            'success': True,
            'booking': booking.to_dict()
        })

    except Exception as e:

        current_app.logger.exception(
            f"GET BOOKING FAILED | id={booking_id} | error={str(e)}"
        )

        return jsonify({
            'success': False,
            'error': 'Unable to retrieve booking'
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@api_bp.route('/health', methods=['GET'])
def health():

    return jsonify({
        'success': True,
        'service': 'booking-api',
        'status': 'online'
    })