from app import db
from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
import uuid


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    name = db.Column(
        db.String(100)
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    last_login = db.Column(
        db.DateTime(timezone=True)
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def check_password(self, password):
        return self.password == password

    def to_dict(self):
        return {
            'id': str(self.id) if self.id else None,
            'username': self.username,
            'name': self.name,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AdminUser {self.username}>'