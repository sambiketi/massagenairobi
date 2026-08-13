from app import db
from datetime import datetime
import uuid

class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            return setting.value
        return default
    
    @classmethod
    def set_setting(cls, key, value):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
        return setting
    
    @classmethod
    def get_settings(cls):
        settings = cls.query.all()
        return {s.key: s.value for s in settings}
    
    @classmethod
    def update_settings(cls, data):
        for key, value in data.items():
            if value is not None:
                cls.set_setting(key, value)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
