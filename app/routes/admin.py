import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from app.models import Therapist, Service, Booking, GalleryImage, BlogPost
from app.models.settings import SiteSetting  
from app.models.admin import AdminUser

# Helper function for safe file replacement
def safe_replace_file(old_url, new_file, folder):
    """
    Safely replace a file: upload new, then delete old.
    Returns the new URL or None if failed.
    """
    if not new_file or not new_file.filename:
        return old_url  # No new file, keep old
    
    result = UploadService.replace_file(old_url, new_file, folder)
    
    if result.get('success'):
        return result.get('url')
    else:
        current_app.logger.error(f"File replacement failed: {result.get('error')}")
        return old_url  # Keep old URL if replacement failed
from app.services.upload_service import UploadService

admin_bp = Blueprint('admin', __name__)

# ==================== AUTH ROUTES ====================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Email and password are required', 'danger')
            return render_template('admin/login.html')
        
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('admin.login'))

# ==================== DASHBOARD ====================

@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard"""
    # Stats
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status='Pending').count()
    confirmed_bookings = Booking.query.filter_by(status='Confirmed').count()
    completed_bookings = Booking.query.filter_by(status='Completed').count()
    
    total_revenue = db.session.query(func.sum(Booking.amount)).filter(
        Booking.status.in_(['Confirmed', 'Completed'])
    ).scalar() or 0
    
    week_start = datetime.utcnow() - timedelta(days=7)
    new_bookings = Booking.query.filter(Booking.created_at >= week_start).count()
    
    active_therapists = Therapist.query.filter_by(is_available=True).count()
    total_therapists = Therapist.query.count()
    total_services = Service.query.filter_by(is_active=True).count()
    
    # Chart data
    chart_data = []
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        count = Booking.query.filter(
            func.date(Booking.appointment_date) == date.date()
        ).count()
        chart_data.append(count)
    
    recent_bookings = Booking.query.order_by(desc(Booking.created_at)).limit(10).all()
    
    stats = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'completed_bookings': completed_bookings,
        'total_revenue': total_revenue,
        'new_bookings': new_bookings,
        'active_therapists': active_therapists,
        'total_therapists': total_therapists,
        'total_services': total_services,
    }
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        chart_data=chart_data,
        recent_bookings=recent_bookings
    )

# ==================== THERAPIST ROUTES ====================

@admin_bp.route('/therapists')
@login_required
def therapists():
    """Therapists management page"""
    therapists = Therapist.query.order_by(Therapist.name).all()
    return render_template('admin/therapists.html', therapists=therapists)

@admin_bp.route('/api/therapist', methods=['POST'])
@login_required
def create_therapist():
    try:
        name = request.form.get('name')
        specialty = request.form.get('specialty')
        bio = request.form.get('bio')
        is_available = request.form.get('is_available') == 'on'
        
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        therapist = Therapist(
            name=name,
            specialty=specialty,
            bio=bio,
            is_available=is_available
        )
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                result = UploadService.upload_image(file, 'therapists', resize=(400, 400))
                if result['success']:
                    therapist.photo_url = result['url']
        
        db.session.add(therapist)
        db.session.commit()
        return jsonify({'success': True, 'therapist': therapist.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/therapist/<therapist_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def therapist_operations(therapist_id):
    therapist = Therapist.query.get_or_404(therapist_id)
    
    if request.method == 'GET':
        return jsonify(therapist.to_dict())
    
    elif request.method == 'PUT':
        try:
            name = request.form.get('name')
            specialty = request.form.get('specialty')
            bio = request.form.get('bio')
            is_available = request.form.get('is_available') == 'on'
            
            if name:
                therapist.name = name
            if specialty:
                therapist.specialty = specialty
            if bio is not None:
                therapist.bio = bio
            therapist.is_available = is_available
            
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename:
                    result = UploadService.upload_image(file, 'therapists', resize=(400, 400))
                    if result['success']:
                        therapist.photo_url = result['url']
            
            db.session.commit()
            return jsonify({'success': True, 'therapist': therapist.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(therapist)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SERVICE ROUTES ====================

@admin_bp.route('/services')
@login_required
def services():
    services = Service.query.order_by(Service.title).all()
    return render_template('admin/services.html', services=services)

@admin_bp.route('/api/service', methods=['POST'])
@login_required
def create_service():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        price_kes = request.form.get('price_kes', type=int)
        duration_minutes = request.form.get('duration_minutes', type=int)
        is_active = request.form.get('is_active') == 'on'
        
        if not title or not price_kes or not duration_minutes:
            return jsonify({'success': False, 'error': 'Title, price, and duration are required'}), 400
        
        service = Service(
            title=title,
            description=description,
            price_kes=price_kes,
            duration_minutes=duration_minutes,
            is_active=is_active
        )
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                result = UploadService.upload_image(file, 'services', resize=(800, 600))
                if result['success']:
                    service.image_url = result['url']
        
        db.session.add(service)
        db.session.commit()
        return jsonify({'success': True, 'service': service.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/service/<service_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def service_operations(service_id):
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'GET':
        return jsonify(service.to_dict())
    
    elif request.method == 'PUT':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            price_kes = request.form.get('price_kes', type=int)
            duration_minutes = request.form.get('duration_minutes', type=int)
            is_active = request.form.get('is_active') == 'on'
            
            if title:
                service.title = title
            if description is not None:
                service.description = description
            if price_kes:
                service.price_kes = price_kes
            if duration_minutes:
                service.duration_minutes = duration_minutes
            service.is_active = is_active
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    result = UploadService.upload_image(file, 'services', resize=(800, 600))
                    if result['success']:
                        service.image_url = result['url']
            
            db.session.commit()
            return jsonify({'success': True, 'service': service.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(service)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# ==================== BOOKING ROUTES ====================

@admin_bp.route('/bookings')
@login_required
def bookings():
    status = request.args.get('status')
    date = request.args.get('date')
    
    query = Booking.query
    
    if status:
        query = query.filter_by(status=status)
    if date:
        query = query.filter_by(appointment_date=datetime.strptime(date, '%Y-%m-%d').date())
    
    bookings = query.order_by(desc(Booking.appointment_date)).all()
    
    stats = {
        'total': Booking.query.count(),
        'pending': Booking.query.filter_by(status='Pending').count(),
        'confirmed': Booking.query.filter_by(status='Confirmed').count(),
        'completed': Booking.query.filter_by(status='Completed').count(),
    }
    
    return render_template('admin/bookings.html', bookings=bookings, stats=stats)

@admin_bp.route('/api/booking/<booking_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def booking_operations(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if request.method == 'GET':
        return jsonify(booking.to_dict())
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            if 'status' in data:
                booking.status = data['status']
            if 'mpesa_reference' in data:
                booking.mpesa_reference = data['mpesa_reference']
            if 'notes' in data:
                booking.notes = data['notes']
            db.session.commit()
            return jsonify({'success': True, 'booking': booking.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(booking)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/booking/<booking_id>/confirm', methods=['PUT'])
@login_required
def confirm_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        booking.status = 'Confirmed'
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== GALLERY ROUTES ====================

@admin_bp.route('/gallery')
@login_required
def gallery():
    images = GalleryImage.query.order_by(GalleryImage.sort_order).all()
    return render_template('admin/gallery.html', gallery_images=images)

@admin_bp.route('/api/gallery', methods=['POST'])
@login_required
def upload_gallery():
    try:
        if 'gallery_images' not in request.files:
            return jsonify({'success': False, 'error': 'No images provided'}), 400
        
        files = request.files.getlist('gallery_images')
        uploaded = []
        
        for file in files:
            if file and file.filename:
                result = UploadService.upload_image(file, 'gallery', resize=(800, 600), create_thumbnail=True)
                if result['success']:
                    gallery_image = GalleryImage(
                        title=file.filename,
                        url=result['url'],
                        thumbnail_url=result.get('thumbnail_url')
                    )
                    db.session.add(gallery_image)
                    uploaded.append(gallery_image.to_dict())
        
        db.session.commit()
        return jsonify({'success': True, 'images': uploaded})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/gallery/<image_id>', methods=['DELETE'])
@login_required
def delete_gallery_image(image_id):
    try:
        image = GalleryImage.query.get_or_404(image_id)
        
        # Try to delete from storage (doesn't fail if file missing)
        if image.url:
            UploadService.delete_file(image.url)
        if image.thumbnail_url:
            UploadService.delete_file(image.thumbnail_url)
        
        db.session.delete(image)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== BLOG CRUD ====================

@admin_bp.route('/blog')
@login_required
def blog():
    posts = BlogPost.query.order_by(desc(BlogPost.created_at)).all()
    return render_template('admin/blog.html', posts=posts)

@admin_bp.route('/api/blog', methods=['POST'])
@login_required
def create_blog_post():
    try:
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        is_published = request.form.get('is_published') == 'on'
        meta_description = request.form.get('meta_description')
        meta_keywords = request.form.get('meta_keywords')
        
        if not title or not content:
            return jsonify({'success': False, 'error': 'Title and content are required'}), 400
        
        if not slug:
            slug = title.lower().replace(' ', '-').replace('.', '').replace(',', '')
            slug = slug.replace("'", '').replace('"', '')
        
        post = BlogPost(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            is_published=is_published,
            meta_description=meta_description,
            meta_keywords=meta_keywords
        )
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                result = UploadService.upload_image(file, 'blog', resize=(1200, 630))
                if result['success']:
                    post.image_url = result['url']
        
        db.session.add(post)
        db.session.commit()
        return jsonify({'success': True, 'post': post.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/blog/<post_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def blog_operations(post_id):
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'GET':
        return jsonify(post.to_dict())
    
    elif request.method == 'PUT':
        try:
            title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            excerpt = request.form.get('excerpt')
            is_published = request.form.get('is_published') == 'on'
            meta_description = request.form.get('meta_description')
            meta_keywords = request.form.get('meta_keywords')
            
            if title:
                post.title = title
            if slug:
                post.slug = slug
            if content:
                post.content = content
            if excerpt is not None:
                post.excerpt = excerpt
            post.is_published = is_published
            if meta_description is not None:
                post.meta_description = meta_description
            if meta_keywords is not None:
                post.meta_keywords = meta_keywords
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    result = UploadService.upload_image(file, 'blog', resize=(1200, 630))
                    if result['success']:
                        post.image_url = result['url']
            
            db.session.commit()
            return jsonify({'success': True, 'post': post.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(post)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SETTINGS ROUTES ====================

@admin_bp.route('/settings')
@login_required
def settings():
    settings = SiteSetting.get_settings()
    gallery_images = GalleryImage.query.order_by(GalleryImage.sort_order).all()
    return render_template('admin/settings.html', settings=settings, gallery_images=gallery_images)

@admin_bp.route('/api/settings', methods=['POST'])
@login_required
def update_settings():
    try:
        data = {
            'business_name': request.form.get('business_name'),
            'business_location': request.form.get('business_location'),
            'business_phone': request.form.get('business_phone'),
            'business_email': request.form.get('business_email'),
            'till_number': request.form.get('till_number'),
            'whatsapp_number': request.form.get('whatsapp_number'),
            'weekday_hours': request.form.get('weekday_hours'),
            'saturday_hours': request.form.get('saturday_hours'),
            'sunday_hours': request.form.get('sunday_hours'),
            'business_tagline': request.form.get('business_tagline'),
            'business_description': request.form.get('business_description'),
            'facebook_url': request.form.get('facebook_url'),
            'instagram_url': request.form.get('instagram_url'),
            'twitter_url': request.form.get('twitter_url'),
            'youtube_url': request.form.get('youtube_url'),
            'meta_title': request.form.get('meta_title'),
            'meta_description': request.form.get('meta_description'),
            'meta_keywords': request.form.get('meta_keywords'),
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        SiteSetting.update_settings(data)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/settings/hero-video', methods=['POST'])
@login_required
def upload_hero_video():
    try:
        if 'hero_video' not in request.files:
            return jsonify({'success': False, 'error': 'No video provided'}), 400
        
        file = request.files['hero_video']
        result = UploadService.upload_video(file, 'hero')
        
        if not result['success']:
            return jsonify({'success': False, 'error': result.get('error')}), 400
        
        SiteSetting.set_setting('hero_video_url', result['url'])
        db.session.commit()
        return jsonify({'success': True, 'url': result['url']})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/settings/hero-video', methods=['DELETE'])
@login_required
def remove_hero_video():
    try:
        old_video = SiteSetting.get_setting('hero_video_url')
        if old_video:
            UploadService.delete_file(old_video)
        SiteSetting.set_setting('hero_video_url', None)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/settings/logo', methods=['POST'])
@login_required
def upload_logo():
    try:
        if 'logo' not in request.files:
            return jsonify({'success': False, 'error': 'No logo provided'}), 400
        
        file = request.files['logo']
        result = UploadService.upload_image(file, 'logo', resize=(200, 200))
        
        if not result['success']:
            return jsonify({'success': False, 'error': result.get('error')}), 400
        
        SiteSetting.set_setting('logo_url', result['url'])
        db.session.commit()
        return jsonify({'success': True, 'url': result['url']})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/settings/logo', methods=['DELETE'])
@login_required
def remove_logo():
    try:
        old_logo = SiteSetting.get_setting('logo_url')
        if old_logo:
            UploadService.delete_file(old_logo)
        SiteSetting.set_setting('logo_url', None)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/settings/background-image', methods=['POST'])
@login_required
def upload_background_image():
    try:
        if 'background_image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        file = request.files['background_image']
        result = UploadService.upload_image(file, 'background', resize=(1920, 1080))
        
        if not result['success']:
            return jsonify({'success': False, 'error': result.get('error')}), 400
        
        SiteSetting.set_setting('background_image_url', result['url'])
        db.session.commit()
        return jsonify({'success': True, 'url': result['url']})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/settings/background-image', methods=['DELETE'])
@login_required
def remove_background_image():
    try:
        old_bg = SiteSetting.get_setting('background_image_url')
        if old_bg:
            UploadService.delete_file(old_bg)
        SiteSetting.set_setting('background_image_url', None)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500





