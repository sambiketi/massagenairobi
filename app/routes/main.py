from flask import Blueprint, render_template, current_app, request
from app.models import Therapist, Service, GalleryImage
from app.models.settings import SiteSetting

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage"""
    try:
        # Get data from database
        therapists = Therapist.query.filter_by(is_available=True).order_by(Therapist.name).all()
        services = Service.query.filter_by(is_active=True).order_by(Service.title).all()
        gallery_images = GalleryImage.query.filter_by(is_active=True).order_by(GalleryImage.sort_order).all()
        
        # Get hero video from settings
        hero_video_url = SiteSetting.get_setting('hero_video_url')
        
        # Get business info from settings
        settings = SiteSetting.get_settings()
        
        return render_template(
            'index.html',
            therapists=therapists,
            services=services,
            gallery_images=gallery_images,
            hero_video={'url': hero_video_url} if hero_video_url else None,
            business_name=settings.get('business_name', current_app.config.get('BUSINESS_NAME')),
            business_location=settings.get('business_location', current_app.config.get('BUSINESS_LOCATION')),
            business_phone=settings.get('business_phone', current_app.config.get('BUSINESS_PHONE')),
            business_email=settings.get('business_email', current_app.config.get('BUSINESS_EMAIL')),
            till_number=settings.get('till_number', current_app.config.get('TILL_NUMBER')),
            whatsapp_number=settings.get('whatsapp_number', current_app.config.get('WHATSAPP_NUMBER'))
        )
    except Exception as e:
        current_app.logger.error(f"Error loading homepage: {str(e)}")
        return render_template('index.html', therapists=[], services=[], gallery_images=[])