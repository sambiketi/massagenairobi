from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Therapist(db.Model):
    __tablename__ = 'therapists'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    specialty = db.Column(
        db.String(150)
    )

    bio = db.Column(
        db.Text
    )

    photo_url = db.Column(
        db.String(500)
    )

    is_available = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            'id': str(self.id) if self.id else None,
            'name': self.name,
            'specialty': self.specialty,
            'bio': self.bio,
            'photo_url': self.photo_url,
            'is_available': self.is_available,
            'created_at': (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }

    def __repr__(self):
        return f'<Therapist {self.name}>'