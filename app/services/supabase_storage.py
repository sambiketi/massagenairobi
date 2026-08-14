import requests
import mimetypes
import socket
from flask import current_app
from urllib.parse import urlparse

class SupabaseStorage:
    """
    Supabase Storage client using REST API.
    """
    
    @staticmethod
    def _get_supabase_url() -> str:
        """Get Supabase URL from config"""
        url = current_app.config.get('SUPABASE_URL', '').rstrip('/')
        if not url:
            raise ValueError("SUPABASE_URL not configured")
        return url
    
    @staticmethod
    def _get_api_key() -> str:
        """Get service-role key from config"""
        key = current_app.config.get('SUPABASE_SERVICE_ROLE_KEY')
        if not key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY not configured")
        return key
    
    @staticmethod
    def _get_headers(content_type: str = None) -> dict:
        """Get headers for Supabase Storage API"""
        headers = {
            'Authorization': f'Bearer {SupabaseStorage._get_api_key()}',
        }
        if content_type:
            headers['Content-Type'] = content_type
        return headers
    
    @staticmethod
    def _get_bucket_for_folder(folder: str) -> str:
        """Map application folder names to Supabase bucket names."""
        mapping = {
            'therapists': 'therapists',
            'services': 'services',
            'gallery': 'gallery',
            'logo': 'logo',
            'background': 'background',
            'blog': 'blog',
            'hero': 'hero',
        }
        
        bucket = mapping.get(folder)
        if not bucket:
            raise ValueError(f"Unknown folder '{folder}'")
        
        return bucket
    
    @staticmethod
    def _test_connection():
        """Test if Supabase is reachable"""
        try:
            supabase_url = SupabaseStorage._get_supabase_url()
            # Try to resolve the hostname
            hostname = supabase_url.replace('https://', '').replace('http://', '').split('/')[0]
            socket.gethostbyname(hostname)
            return True
        except Exception as e:
            current_app.logger.error(f"DNS resolution failed for {hostname}: {str(e)}")
            return False
    
    @staticmethod
    def upload_file(file, folder: str, filename: str) -> dict:
        """
        Upload a file to Supabase Storage.
        """
        try:
            supabase_url = SupabaseStorage._get_supabase_url()
            bucket = SupabaseStorage._get_bucket_for_folder(folder)
            
            # Test connection first
            if not SupabaseStorage._test_connection():
                return {
                    'success': False,
                    'error': f"Cannot reach Supabase. Please check your network and SUPABASE_URL: {supabase_url}"
                }
            
            # Read file content
            file.seek(0)
            file_content = file.read()
            file_size = len(file_content)
            
            # Determine content type
            content_type = file.content_type or mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Upload to Supabase Storage via REST API
            url = f"{supabase_url}/storage/v1/object/{bucket}/{filename}"
            headers = SupabaseStorage._get_headers(content_type)
            
            current_app.logger.info(f"📤 Uploading to: {url}")
            current_app.logger.info(f"📤 Bucket: {bucket}, Filename: {filename}, Size: {file_size} bytes")
            
            response = requests.post(
                url,
                headers=headers,
                data=file_content,
                timeout=30
            )
            
            current_app.logger.info(f"📤 Response status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{filename}"
                current_app.logger.info(f"✅ Upload successful: {public_url}")
                
                return {
                    'success': True,
                    'url': public_url,
                    'size': file_size,
                    'bucket': bucket,
                    'filename': filename
                }
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg = error_data['message']
                    elif 'error' in error_data:
                        error_msg = error_data['error']
                except:
                    pass
                
                current_app.logger.error(f"❌ Supabase upload failed: {response.status_code} - {error_msg}")
                return {
                    'success': False,
                    'error': f"Upload failed ({response.status_code}): {error_msg}",
                    'status_code': response.status_code
                }
                
        except requests.exceptions.ConnectionError as e:
            current_app.logger.error(f"❌ Connection error: {str(e)}")
            return {
                'success': False,
                'error': f"Cannot connect to Supabase. Please check your SUPABASE_URL: {str(e)}"
            }
        except requests.exceptions.Timeout:
            current_app.logger.error(f"❌ Timeout error")
            return {
                'success': False,
                'error': "Connection to Supabase timed out. Please try again."
            }
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"❌ Request error: {str(e)}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            current_app.logger.error(f"❌ Upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_file(file_url: str) -> dict:
        """Delete a file from Supabase Storage."""
        try:
            supabase_url = SupabaseStorage._get_supabase_url()
            
            if not file_url.startswith(supabase_url):
                return {'success': True, 'skipped': True}
            
            prefix = f"{supabase_url}/storage/v1/object/public/"
            if not file_url.startswith(prefix):
                return {'success': True, 'skipped': True}
            
            bucket_path = file_url[len(prefix):]
            parts = bucket_path.split('/', 1)
            if len(parts) != 2:
                return {'success': True, 'skipped': True}
            
            bucket, path = parts[0], parts[1]
            
            url = f"{supabase_url}/storage/v1/object/{bucket}/{path}"
            headers = SupabaseStorage._get_headers()
            
            response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code in [200, 204]:
                current_app.logger.info(f"✅ Deleted: {file_url}")
                return {'success': True}
            else:
                current_app.logger.warning(f"Delete warning: {response.status_code}")
                return {'success': True, 'warn': True}
                
        except Exception as e:
            current_app.logger.error(f"Delete error: {str(e)}")
            return {'success': True, 'warn': True}
