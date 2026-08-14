import os
import uuid
from datetime import datetime
from flask import current_app
from app.services.supabase_storage import SupabaseStorage

class UploadService:
    """
    File upload service using Supabase Storage.
    No local filesystem storage used.
    """
    
    @staticmethod
    def allowed_file(filename, allowed_extensions=None):
        """Check if file extension is allowed"""
        if allowed_extensions is None:
            allowed_extensions = current_app.config.get(
                'ALLOWED_EXTENSIONS', 
                {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            )
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def generate_filename(original_filename):
        """
        Generate unique filename with timestamp and UUID.
        Preserves original extension.
        """
        ext = ''
        if '.' in original_filename:
            ext = original_filename.rsplit('.', 1)[1].lower()
        
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        if ext:
            return f"{timestamp}_{unique_id}.{ext}"
        return f"{timestamp}_{unique_id}"
    
    @staticmethod
    def upload_image(file, folder='uploads', resize=None, create_thumbnail=False):
        """
        Upload an image to Supabase Storage.
        
        Args:
            file: File object from request
            folder: Logical folder name (therapists, services, gallery, etc.)
            resize: NOT SUPPORTED (kept for API compatibility)
            create_thumbnail: NOT SUPPORTED (kept for API compatibility)
        
        Returns:
            dict: {success: bool, url: str, thumbnail_url: str, size: int, error: str}
        """
        try:
            # Validate file
            if not file or not file.filename:
                return {'success': False, 'error': 'No file provided'}
            
            if not UploadService.allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif', 'webp'}):
                return {
                    'success': False, 
                    'error': 'Image format not allowed. Allowed: png, jpg, jpeg, gif, webp'
                }
            
            # Generate unique filename
            filename = UploadService.generate_filename(file.filename)
            
            # Upload to Supabase Storage
            result = SupabaseStorage.upload_file(file, folder, filename)
            
            if not result.get('success'):
                return {
                    'success': False,
                    'error': result.get('error', 'Upload failed')
                }
            
            # For gallery, we need thumbnail_url (use same URL for now)
            thumbnail_url = None
            if create_thumbnail:
                thumbnail_url = result.get('url')
            
            return {
                'success': True,
                'url': result.get('url'),
                'thumbnail_url': thumbnail_url,
                'filename': filename,
                'bucket': result.get('bucket'),
                'size': result.get('size', 0)
            }
            
        except ValueError as e:
            current_app.logger.error(f"Upload configuration error: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            current_app.logger.error(f"Upload error: {str(e)}")
            return {'success': False, 'error': f'Upload failed: {str(e)}'}
    
    @staticmethod
    def upload_video(file, folder='uploads'):
        """
        Upload a video to Supabase Storage.
        
        Args:
            file: File object from request
            folder: Logical folder name (hero, etc.)
        
        Returns:
            dict: {success: bool, url: str, size: int, error: str}
        """
        try:
            # Validate file
            if not file or not file.filename:
                return {'success': False, 'error': 'No file provided'}
            
            if not UploadService.allowed_file(file.filename, {'mp4', 'mov', 'webm'}):
                return {
                    'success': False,
                    'error': 'Video format not allowed. Allowed: mp4, mov, webm'
                }
            
            # Generate unique filename
            filename = UploadService.generate_filename(file.filename)
            
            # Upload to Supabase Storage
            result = SupabaseStorage.upload_file(file, folder, filename)
            
            if not result.get('success'):
                return {
                    'success': False,
                    'error': result.get('error', 'Upload failed')
                }
            
            return {
                'success': True,
                'url': result.get('url'),
                'filename': filename,
                'bucket': result.get('bucket'),
                'size': result.get('size', 0)
            }
            
        except ValueError as e:
            current_app.logger.error(f"Upload configuration error: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            current_app.logger.error(f"Video upload error: {str(e)}")
            return {'success': False, 'error': f'Upload failed: {str(e)}'}
    
    @staticmethod
    def delete_file(file_url: str) -> dict:
        """
        Delete a file from Supabase Storage.
        Safe for legacy URLs - skips them without error.
        
        Returns:
            dict: {success: bool, skipped: bool, warn: bool, message: str}
        """
        return SupabaseStorage.delete_file(file_url)
    
    @staticmethod
    def replace_file(file_url: str, file, folder: str) -> dict:
        """
        Replace an existing file with a new one.
        Safe sequence: upload new -> confirm -> delete old.
        
        Args:
            file_url: URL of the old file to replace
            file: New file object
            folder: Logical folder name
        
        Returns:
            dict: {success: bool, old_deleted: bool, url: str, error: str}
        """
        try:
            # Step 1: Upload new file first
            upload_result = UploadService.upload_image(file, folder)
            
            if not upload_result.get('success'):
                return {
                    'success': False,
                    'error': upload_result.get('error', 'Upload failed')
                }
            
            # Step 2: Only delete old file if upload succeeded
            old_deleted = False
            if file_url:
                delete_result = UploadService.delete_file(file_url)
                old_deleted = delete_result.get('success', False)
            
            return {
                'success': True,
                'url': upload_result.get('url'),
                'size': upload_result.get('size', 0),
                'old_deleted': old_deleted
            }
            
        except Exception as e:
            current_app.logger.error(f"Replace file error: {str(e)}")
            return {'success': False, 'error': str(e)}
