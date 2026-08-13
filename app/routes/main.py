from flask import Blueprint, render_template, current_app, request
from app.models import Therapist, Service, GalleryImage
from app.models.settings import SiteSetting

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        therapists = Therapist.query.filter_by(is_available=True).order_by(Therapist.name).all()
        services = Service.query.filter_by(is_active=True).order_by(Service.title).all()
        gallery_images = GalleryImage.query.filter_by(is_active=True).order_by(GalleryImage.sort_order).all()
        
        hero_video_url = SiteSetting.get_setting('hero_video_url')
        logo_url = SiteSetting.get_setting('logo_url')
        settings = SiteSetting.get_settings()
        
        return render_template(
            'index.html',
            therapists=therapists,
            services=services,
            gallery_images=gallery_images,
            hero_video={'url': hero_video_url} if hero_video_url else None,
            logo_url=logo_url,
            business_name=settings.get('business_name', current_app.config.get('BUSINESS_NAME')),
            business_location=settings.get('business_location', current_app.config.get('BUSINESS_LOCATION')),
            business_phone=settings.get('business_phone', current_app.config.get('BUSINESS_PHONE')),
            business_email=settings.get('business_email', current_app.config.get('BUSINESS_EMAIL')),
            till_number=settings.get('till_number', current_app.config.get('TILL_NUMBER')),
            whatsapp_number=settings.get('whatsapp_number', current_app.config.get('WHATSAPP_NUMBER')),
            business_tagline=settings.get('business_tagline', 'Premium Massage Therapy in Nairobi West'),
            business_description=settings.get('business_description', 'Experience the ultimate relaxation with our professional massage therapists.')
        )
    except Exception as e:
        current_app.logger.error(f"Error loading homepage: {str(e)}")
        return render_template('index.html', therapists=[], services=[], gallery_images=[])

@main_bp.route('/therapists')
def therapists_page():
    therapists = Therapist.query.filter_by(is_available=True).order_by(Therapist.name).all()
    settings = SiteSetting.get_settings()
    logo_url = SiteSetting.get_setting('logo_url')
    
    return render_template(
        'therapists.html',
        therapists=therapists,
        logo_url=logo_url,
        business_name=settings.get('business_name', current_app.config.get('BUSINESS_NAME'))
    )

@main_bp.route('/about')
def about_page():
    settings = SiteSetting.get_settings()
    logo_url = SiteSetting.get_setting('logo_url')
    gallery_images = GalleryImage.query.filter_by(is_active=True).order_by(GalleryImage.sort_order).all()
    
    return render_template(
        'about.html',
        logo_url=logo_url,
        business_name=settings.get('business_name', current_app.config.get('BUSINESS_NAME')),
        business_location=settings.get('business_location', current_app.config.get('BUSINESS_LOCATION')),
        business_phone=settings.get('business_phone', current_app.config.get('BUSINESS_PHONE')),
        business_email=settings.get('business_email', current_app.config.get('BUSINESS_EMAIL')),
        business_description=settings.get('business_description', ''),
        gallery_images=gallery_images,
        weekday_hours=settings.get('weekday_hours', '9:00 AM - 9:00 PM'),
        saturday_hours=settings.get('saturday_hours', '9:00 AM - 9:00 PM'),
        sunday_hours=settings.get('sunday_hours', '10:00 AM - 6:00 PM')
    )
