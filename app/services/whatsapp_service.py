import urllib.parse
from flask import current_app

class WhatsAppService:
    """Service for WhatsApp integration"""
    
    @staticmethod
    def generate_booking_confirmation_link(booking_data):
        """Generate WhatsApp link with booking details"""
        phone_number = current_app.config.get('WHATSAPP_NUMBER', '254700000000')
        
        message = f"""Hello, I have made a booking request:

Booking Details:
- Name: {booking_data.get('client_name')}
- Phone: {booking_data.get('client_phone')}
- Date: {booking_data.get('appointment_date')} at {booking_data.get('appointment_time')}
- Service: {booking_data.get('service_title', 'Massage')}
- Therapist: {booking_data.get('therapist_name', 'Not specified')}
- M-Pesa Ref: {booking_data.get('mpesa_reference', 'Pending')}

Please confirm my booking. Thank you!"""
        
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{phone_number}?text={encoded_message}"