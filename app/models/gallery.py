from app import db
from datetime import datetime

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(db.uuid.uuid4()))
    title = db.Column(db.String(100))
    url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'thumbnail_url': self.thumbnail_url,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }