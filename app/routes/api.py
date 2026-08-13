from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app import db
from app.models import Booking, Therapist, Service
from app.services.whatsapp_service import WhatsAppService

api_bp = Blueprint('api', __name__)

@api_bp.route('/book', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'phone', 'date', 'time']
        for field in required:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Parse date and time
        try:
            appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date or time format'
            }), 400
        
        # Get therapist and service
        therapist = None
        service = None
        amount = 0
        
        if data.get('therapist_id'):
            therapist = Therapist.query.get(data['therapist_id'])
        
        if data.get('service_id'):
            service = Service.query.get(data['service_id'])
            if service:
                amount = service.price_kes
        
        # Create booking
        booking = Booking(
            client_name=data['name'],
            client_phone=data['phone'],
            client_email=data.get('email'),
            therapist_id=data.get('therapist_id'),
            service_id=data.get('service_id'),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            mpesa_reference=data.get('mpesa_code', 'PENDING_TILL'),
            amount=amount,
            notes=data.get('notes'),
            status='Pending'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Generate WhatsApp confirmation link
        whatsapp_url = WhatsAppService.generate_booking_confirmation_link({
            'client_name': booking.client_name,
            'client_phone': booking.client_phone,
            'appointment_date': booking.appointment_date,
            'appointment_time': booking.appointment_time.strftime('%H:%M'),
            'mpesa_reference': booking.mpesa_reference,
            'service_title': service.title if service else 'Massage',
            'therapist_name': therapist.name if therapist else 'Not specified'
        })
        
        return jsonify({
            'success': True,
            'booking_id': booking.id,
            'whatsapp_url': whatsapp_url,
            'message': 'Booking created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Booking error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@api_bp.route('/therapists', methods=['GET'])
def get_therapists():
    """Get all available therapists"""
    therapists = Therapist.query.filter_by(is_available=True).order_by(Therapist.name).all()
    return jsonify([t.to_dict() for t in therapists])

@api_bp.route('/services', methods=['GET'])
def get_services():
    """Get all active services"""
    services = Service.query.filter_by(is_active=True).order_by(Service.title).all()
    return jsonify([s.to_dict() for s in services])

@api_bp.route('/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get booking details"""
    booking = Booking.query.get_or_404(booking_id)
    return jsonify(booking.to_dict())