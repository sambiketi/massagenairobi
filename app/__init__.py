import os
import uuid
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
#from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
#csrf = CSRFProtect()
cors = CORS()
db.uuid = uuid

def create_app(config_name=None):
    app = Flask(__name__)
    from app.config.settings import Config, DevelopmentConfig, ProductionConfig, TestingConfig
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    elif env == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    if config_name:
        app.config.from_object(config_name)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message_category = 'info'
   # csrf.init_app(app)
    cors.init_app(app)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404
    @app.errorhandler(500)
    def server_error(error):
        return {"error": "Internal server error"}, 500
    @app.errorhandler(413)
    def too_large(error):
        return {"error": "File too large"}, 413
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.admin import AdminUser
    return AdminUser.query.get(user_id)
