from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from app import db
from app.models import Booking, Service
from app.services.whatsapp_service import WhatsAppService


api_bp = Blueprint('api', __name__)


# ============================================================
# CREATE BOOKING
# ============================================================

@api_bp.route('/book', methods=['POST'])
def create_booking():

    try:

        # ----------------------------------------------------
        # READ JSON
        # ----------------------------------------------------

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                'success': False,
                'error': 'Invalid or missing JSON data'
            }), 400

        # ----------------------------------------------------
        # REQUIRED FIELDS
        #
        # These match:
        # 1. The HTML form
        # 2. The Booking model
        # 3. The database
        # ----------------------------------------------------

        required_fields = [
            'client_name',
            'client_phone',
            'appointment_date',
            'appointment_time',
            'service_id'
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
        # CLEAN INPUT
        # ----------------------------------------------------

        client_name = str(
            data.get('client_name')
        ).strip()

        client_phone = str(
            data.get('client_phone')
        ).strip()

        service_id = str(
            data.get('service_id')
        ).strip()

        date_value = str(
            data.get('appointment_date')
        ).strip()

        time_value = str(
            data.get('appointment_time')
        ).strip()

        notes = data.get('notes')

        mpesa_reference = data.get(
            'mpesa_reference'
        )

        if notes:

            notes = str(
                notes
            ).strip()

        if mpesa_reference:

            mpesa_reference = str(
                mpesa_reference
            ).strip()

        # ----------------------------------------------------
        # VALIDATE CLIENT NAME
        # ----------------------------------------------------

        if len(client_name) < 2:

            return jsonify({
                'success': False,
                'error': 'Please provide a valid name'
            }), 400

        # ----------------------------------------------------
        # VALIDATE PHONE
        # ----------------------------------------------------

        if len(client_phone) < 7:

            return jsonify({
                'success': False,
                'error': 'Please provide a valid phone number'
            }), 400

        # ----------------------------------------------------
        # FIND SERVICE
        # ----------------------------------------------------

        service = Service.query.filter_by(
            id=service_id,
            is_active=True
        ).first()

        if not service:

            return jsonify({
                'success': False,
                'error': 'Selected service is not available'
            }), 400

        # ----------------------------------------------------
        # PARSE APPOINTMENT DATE
        # ----------------------------------------------------

        try:

            appointment_date = datetime.strptime(
                date_value,
                '%Y-%m-%d'
            ).date()

        except (ValueError, TypeError):

            return jsonify({
                'success': False,
                'error':
                    'Invalid appointment date. Use YYYY-MM-DD.'
            }), 400

        # ----------------------------------------------------
        # PARSE APPOINTMENT TIME
        # ----------------------------------------------------

        try:

            appointment_time = datetime.strptime(
                time_value,
                '%H:%M'
            ).time()

        except (ValueError, TypeError):

            return jsonify({
                'success': False,
                'error':
                    'Invalid appointment time. Use HH:MM.'
            }), 400

        # ----------------------------------------------------
        # PREVENT PAST BOOKINGS
        # ----------------------------------------------------

        now = datetime.now()

        appointment_datetime = datetime.combine(
            appointment_date,
            appointment_time
        )

        if appointment_datetime < now:

            return jsonify({
                'success': False,
                'error':
                    'You cannot book a date or time in the past'
            }), 400

        # ----------------------------------------------------
        # PREVENT DOUBLE BOOKINGS
        #
        # Only Pending and Confirmed appointments block
        # the time slot.
        #
        # Completed and Cancelled appointments do not.
        # ----------------------------------------------------

        existing_booking = Booking.query.filter_by(
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).filter(
            Booking.status.in_([
                'Pending',
                'Confirmed'
            ])
        ).first()

        if existing_booking:

            return jsonify({
                'success': False,
                'error':
                    'That time slot is already booked. '
                    'Please choose another time.'
            }), 409

        # ----------------------------------------------------
        # CREATE BOOKING OBJECT
        # ----------------------------------------------------

        booking = Booking(

            client_name=client_name,

            client_phone=client_phone,

            service_id=service.id,

            appointment_date=appointment_date,

            appointment_time=appointment_time,

            mpesa_reference=mpesa_reference,

            amount=service.price_kes,

            status='Pending',

            notes=notes
        )

        # ----------------------------------------------------
        # SAVE BOOKING TO DATABASE
        # ----------------------------------------------------

        db.session.add(
            booking
        )

        db.session.commit()

        # ----------------------------------------------------
        # LOG SUCCESS
        # ----------------------------------------------------

        current_app.logger.info(
            f"BOOKING CREATED | "
            f"id={booking.id} | "
            f"name={booking.client_name} | "
            f"phone={booking.client_phone} | "
            f"service={service.title} | "
            f"date={booking.appointment_date} | "
            f"time={booking.appointment_time} | "
            f"status={booking.status}"
        )

        # ----------------------------------------------------
        # GENERATE WHATSAPP CONFIRMATION
        # ----------------------------------------------------

        whatsapp_url = None

        try:

            whatsapp_url = (
                WhatsAppService
                .generate_booking_confirmation_link({

                    'client_name':
                        booking.client_name,

                    'client_phone':
                        booking.client_phone,

                    'appointment_date':
                        booking.appointment_date,

                    'appointment_time':
                        booking.appointment_time.strftime(
                            '%H:%M'
                        ),

                

                    'service_title':
                        service.title

                })
            )

        except Exception as whatsapp_error:

            current_app.logger.warning(
                f"WhatsApp link generation failed: "
                f"{whatsapp_error}"
            )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return jsonify({

            'success': True,

            'message':
                'Booking created successfully',

            'booking_id':
                str(booking.id),

            'booking':
                booking.to_dict(),

            'whatsapp_url':
                whatsapp_url

        }), 201

    # ========================================================
    # DATABASE / UNEXPECTED ERROR
    # ========================================================

    except Exception as e:

        db.session.rollback()

        current_app.logger.exception(
            f"BOOKING CREATION FAILED: {str(e)}"
        )

        return jsonify({

            'success': False,

            'error':
                'Unable to create booking',

            'debug':
                str(e)
                if current_app.debug
                else None

        }), 500


# ============================================================
# GET AVAILABLE SERVICES
# ============================================================

@api_bp.route('/services', methods=['GET'])
def get_services():

    try:

        services = Service.query.filter_by(
            is_active=True
        ).order_by(
            Service.title.asc()
        ).all()

        return jsonify({

            'success': True,

            'services': [
                service.to_dict()
                for service in services
            ]

        })

    except Exception as e:

        current_app.logger.exception(
            f"GET SERVICES FAILED: {str(e)}"
        )

        return jsonify({

            'success': False,

            'error':
                'Unable to retrieve services'

        }), 500


# ============================================================
# GET SINGLE BOOKING
# ============================================================

@api_bp.route(
    '/bookings/<booking_id>',
    methods=['GET']
)
def get_booking(booking_id):

    try:

        booking = Booking.query.get(
            booking_id
        )

        if not booking:

            return jsonify({

                'success': False,

                'error':
                    'Booking not found'

            }), 404

        return jsonify({

            'success': True,

            'booking':
                booking.to_dict()

        })

    except Exception as e:

        current_app.logger.exception(

            f"GET BOOKING FAILED | "
            f"id={booking_id} | "
            f"error={str(e)}"

        )

        return jsonify({

            'success': False,

            'error':
                'Unable to retrieve booking'

        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@api_bp.route(
    '/health',
    methods=['GET']
)
def health():

    return jsonify({

        'success': True,

        'service':
            'booking-api',

        'status':
            'online'

    })