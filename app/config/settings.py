import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration from environment variables"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError("SECRET_KEY must be set in environment variables for production")
        else:
            SECRET_KEY = 'dev-secret-key-do-not-use-in-production'
            print("⚠️  WARNING: Using default SECRET_KEY for development")
    
    # Database - Using DATABASE_URL from Render session pooler
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL must be set in environment variables")
    
    # Force psycopg3
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
    elif DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLAlchemy Engine with pooler settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,
        'pool_reset_on_return': 'rollback',
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'connect_args': {
            'connect_timeout': int(os.environ.get('DB_CONNECT_TIMEOUT', 10)),
            'keepalives': 1,
            'keepalives_idle': int(os.environ.get('DB_KEEPALIVE_IDLE', 30)),
            'keepalives_interval': int(os.environ.get('DB_KEEPALIVE_INTERVAL', 10)),
            'keepalives_count': int(os.environ.get('DB_KEEPALIVE_COUNT', 5)),
        }
    }
    
    # Business
    BUSINESS_NAME = os.environ.get('BUSINESS_NAME', 'Sanctuary Massage')
    BUSINESS_LOCATION = os.environ.get('BUSINESS_LOCATION')
    BUSINESS_PHONE = os.environ.get('BUSINESS_PHONE')
    BUSINESS_EMAIL = os.environ.get('BUSINESS_EMAIL')
    TILL_NUMBER = os.environ.get('TILL_NUMBER')
    WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER')
    
    # Admin (for initial setup only)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    
    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'webm'}

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
