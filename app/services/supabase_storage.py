import requests
import mimetypes
from flask import current_app
from urllib.parse import urlparse

class SupabaseStorage:
    """
    Supabase Storage client using REST API.
    Uses only requests (already in dependencies).
    Service-role key stays server-side only.
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
        """Get service-role key from config (server-side only)"""
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
        """
        Map application folder names to Supabase bucket names.
        This prevents accidental uploads to wrong buckets.
        """
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
            raise ValueError(f"Unknown folder '{folder}'. Must be one of: {', '.join(mapping.keys())}")
        
        return bucket
    
    @staticmethod
    def upload_file(file, folder: str, filename: str) -> dict:
        """
        Upload a file to Supabase Storage.
        
        Args:
            file: File object from request (with .read() method)
            folder: Logical folder name (therapists, services, gallery, etc.)
            filename: Unique filename to use in storage
        
        Returns:
            dict: {success: bool, url: str, size: int, error: str}
        """
        try:
            supabase_url = SupabaseStorage._get_supabase_url()
            bucket = SupabaseStorage._get_bucket_for_folder(folder)
            
            # Read file content (store in memory for size calculation)
            file.seek(0)
            file_content = file.read()
            file_size = len(file_content)
            
            # Determine content type
            content_type = file.content_type or mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Upload to Supabase Storage via REST API
            # API: POST /storage/v1/object/{bucket}/{path}
            url = f"{supabase_url}/storage/v1/object/{bucket}/{filename}"
            headers = SupabaseStorage._get_headers(content_type)
            
            response = requests.post(
                url,
                headers=headers,
                data=file_content,
                timeout=60
            )
            
            # Check response
            if response.status_code == 200 or response.status_code == 201:
                public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{filename}"
                
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
                except:
                    pass
                
                current_app.logger.error(f"Supabase upload failed: {response.status_code} - {error_msg}")
                return {
                    'success': False,
                    'error': f"Upload failed: {error_msg}",
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Supabase upload request error: {str(e)}")
            return {'success': False, 'error': f"Network error: {str(e)}"}
        except Exception as e:
            current_app.logger.error(f"Supabase upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_file(file_url: str) -> dict:
        """
        Delete a file from Supabase Storage.
        
        Args:
            file_url: Full public URL of the file
        
        Returns:
            dict: {success: bool, skipped: bool (if legacy file), error: str}
        """
        try:
            supabase_url = SupabaseStorage._get_supabase_url()
            
            # Skip if not a Supabase URL (legacy local file)
            if not file_url.startswith(supabase_url):
                return {'success': True, 'skipped': True, 'reason': 'legacy_local_file'}
            
            # Parse URL to extract bucket and path
            prefix = f"{supabase_url}/storage/v1/object/public/"
            
            if not file_url.startswith(prefix):
                return {
                    'success': False, 
                    'error': f"URL does not match expected Supabase public URL pattern: {file_url}"
                }
            
            bucket_path = file_url[len(prefix):]
            
            parts = bucket_path.split('/', 1)
            if len(parts) != 2:
                return {
                    'success': False,
                    'error': f"Could not parse bucket/path from URL: {file_url}"
                }
            
            bucket, path = parts[0], parts[1]
            
            # Delete via REST API
            url = f"{supabase_url}/storage/v1/object/{bucket}/{path}"
            headers = SupabaseStorage._get_headers()
            
            response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code in [200, 204]:
                return {'success': True, 'bucket': bucket, 'path': path}
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg = error_data['message']
                except:
                    pass
                
                current_app.logger.warning(f"Supabase delete failed: {response.status_code} - {error_msg}")
                return {
                    'success': True,
                    'warn': True,
                    'message': f"File may not exist or already deleted: {error_msg}"
                }
                
        except Exception as e:
            current_app.logger.error(f"Supabase delete error: {str(e)}")
            return {
                'success': True,
                'warn': True,
                'message': f"Delete error: {str(e)}"
            }
    
    @staticmethod
    def file_exists(file_url: str) -> bool:
        """
        Check if a file exists in Supabase Storage.
        """
        try:
            supabase_url = SupabaseStorage._get_supabase_url()
            
            if not file_url.startswith(supabase_url):
                return False
            
            prefix = f"{supabase_url}/storage/v1/object/public/"
            bucket_path = file_url[len(prefix):]
            parts = bucket_path.split('/', 1)
            
            if len(parts) != 2:
                return False
            
            bucket, path = parts[0], parts[1]
            
            url = f"{supabase_url}/storage/v1/object/public/{bucket}/{path}"
            headers = SupabaseStorage._get_headers()
            
            response = requests.head(url, headers=headers, timeout=10)
            return response.status_code == 200
            
        except:
            return False
