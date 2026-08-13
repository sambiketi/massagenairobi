from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Therapist(db.Model):
    __tablename__ = 'therapists'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(db.uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(150))
    bio = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    bookings = relationship('Booking', backref='therapist', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialty': self.specialty,
            'bio': self.bio,
            'photo_url': self.photo_url,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Therapist {self.name}>'