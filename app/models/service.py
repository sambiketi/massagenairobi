from app import db
from datetime import datetime
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_kes = db.Column(db.Integer, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    bookings = relationship(
        'Booking',
        backref='service',
        lazy=True
    )

    def to_dict(self):
        return {
            'id': str(self.id) if self.id else None,
            'title': self.title,
            'description': self.description,
            'price_kes': self.price_kes,
            'duration_minutes': self.duration_minutes,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }

    def __repr__(self):
        return f'<Service {self.title}>'