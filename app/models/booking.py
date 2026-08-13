from app import db
from datetime import datetime
from sqlalchemy import ForeignKey

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(db.uuid.uuid4()))
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    client_email = db.Column(db.String(100))
    
    therapist_id = db.Column(db.String(36), ForeignKey('therapists.id', ondelete='SET NULL'))
    service_id = db.Column(db.String(36), ForeignKey('services.id', ondelete='SET NULL'))
    
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    
    mpesa_reference = db.Column(db.String(50))
    amount = db.Column(db.Integer, default=0)
    
    status = db.Column(db.String(20), default='Pending')
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_name': self.client_name,
            'client_phone': self.client_phone,
            'client_email': self.client_email,
            'therapist_id': self.therapist_id,
            'therapist_name': self.therapist.name if self.therapist else None,
            'service_id': self.service_id,
            'service_title': self.service.title if self.service else None,
            'amount': self.amount,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'mpesa_reference': self.mpesa_reference,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Booking {self.client_name} - {self.appointment_date}>'