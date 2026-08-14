from app import db
from datetime import datetime
import uuid


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Customer
    client_name = db.Column(
        db.String(100),
        nullable=False
    )

    client_phone = db.Column(
        db.String(20),
        nullable=False
    )

    # Service
    service_id = db.Column(
        db.String(36),
        db.ForeignKey('services.id', ondelete='SET NULL'),
        nullable=True
    )

    service = db.relationship(
        'Service',
        backref='bookings',
        lazy=True
    )

    # Appointment
    appointment_date = db.Column(
        db.Date,
        nullable=False
    )

    appointment_time = db.Column(
        db.Time,
        nullable=False
    )

    # Internal booking management
    status = db.Column(
        db.String(20),
        nullable=False,
        default='Pending'
    )

    amount = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    mpesa_reference = db.Column(
        db.String(50),
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    # Timestamps
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            'id': self.id,
            'client_name': self.client_name,
            'client_phone': self.client_phone,

            'service_id': self.service_id,
            'service_title': (
                self.service.title
                if self.service
                else None
            ),

            'appointment_date': (
                self.appointment_date.isoformat()
                if self.appointment_date
                else None
            ),

            'appointment_time': (
                self.appointment_time.strftime('%H:%M')
                if self.appointment_time
                else None
            ),

            'status': self.status,
            'amount': self.amount,
            'mpesa_reference': self.mpesa_reference,
            'notes': self.notes,

            'created_at': (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),

            'updated_at': (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            )
        }

    def __repr__(self):
        return (
            f'<Booking {self.client_name} '
            f'- {self.appointment_date} '
            f'{self.appointment_time}>'
        )