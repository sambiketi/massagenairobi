import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image

class UploadService:
    """File upload service with image resizing"""
    
    @staticmethod
    def allowed_file(filename, allowed_extensions=None):
        if allowed_extensions is None:
            allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def generate_filename(original_filename):
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{timestamp}_{unique_id}.{ext}"
    
    @staticmethod
    def upload_image(file, folder='uploads', resize=None, create_thumbnail=False):
        try:
            if not file or not file.filename:
                return {'success': False, 'error': 'No file provided'}
            
            if not UploadService.allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif', 'webp'}):
                return {'success': False, 'error': 'Image format not allowed'}
            
            filename = UploadService.generate_filename(file.filename)
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
            os.makedirs(upload_folder, exist_ok=True)
            
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            # Process image
            img = Image.open(filepath)
            
            if resize and isinstance(resize, tuple) and len(resize) == 2:
                img.thumbnail(resize, Image.Resampling.LANCZOS)
                img.save(filepath, quality=85, optimize=True)
            
            thumbnail_url = None
            if create_thumbnail:
                thumb_filename = f"thumb_{filename}"
                thumb_path = os.path.join(upload_folder, thumb_filename)
                thumb = Image.open(filepath)
                thumb.thumbnail((300, 300), Image.Resampling.LANCZOS)
                thumb.save(thumb_path, quality=80, optimize=True)
                thumbnail_url = f"/static/uploads/{folder}/{thumb_filename}"
            
            url = f"/static/uploads/{folder}/{filename}"
            
            return {
                'success': True,
                'url': url,
                'thumbnail_url': thumbnail_url,
                'filename': filename,
                'path': filepath,
                'size': os.path.getsize(filepath)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def upload_video(file, folder='uploads'):
        try:
            if not file or not file.filename:
                return {'success': False, 'error': 'No file provided'}
            
            if not UploadService.allowed_file(file.filename, {'mp4', 'mov', 'webm'}):
                return {'success': False, 'error': 'Video format not allowed'}
            
            filename = UploadService.generate_filename(file.filename)
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
            os.makedirs(upload_folder, exist_ok=True)
            
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            return {
                'success': True,
                'url': f"/static/uploads/{folder}/{filename}",
                'filename': filename,
                'path': filepath,
                'size': os.path.getsize(filepath)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}