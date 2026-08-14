import requests
import mimetypes
from flask import current_app
from urllib.parse import quote, urlparse


class SupabaseStorage:
    """
    Supabase Storage client using the Supabase REST API.
    """

    # ============================================================
    # CONFIG
    # ============================================================

    @staticmethod
    def _get_supabase_url() -> str:
        """Get and validate Supabase project URL."""
        url = current_app.config.get("SUPABASE_URL", "").strip().rstrip("/")

        if not url:
            raise ValueError("SUPABASE_URL not configured")

        if not url.startswith(("http://", "https://")):
            raise ValueError(
                f"SUPABASE_URL must start with http:// or https://. "
                f"Current value: {url}"
            )

        parsed = urlparse(url)

        if not parsed.hostname:
            raise ValueError(f"Invalid SUPABASE_URL: {url}")

        return url

    @staticmethod
    def _get_api_key() -> str:
        """Get Supabase service-role key."""
        key = current_app.config.get("SUPABASE_SERVICE_ROLE_KEY")

        if not key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY not configured"
            )

        return key.strip()

    # ============================================================
    # HEADERS
    # ============================================================

    @staticmethod
    def _get_headers(content_type=None) -> dict:
        """
        Build Supabase API headers.

        IMPORTANT:
        Never log these headers because they contain the service-role key.
        """

        key = SupabaseStorage._get_api_key()

        headers = {
            "Authorization": f"Bearer {key}",
            "apikey": key,
        }

        if content_type:
            headers["Content-Type"] = content_type

        return headers

    # ============================================================
    # BUCKET MAPPING
    # ============================================================

    @staticmethod
    def _get_bucket_for_folder(folder: str) -> str:
        """Map application folders to Supabase Storage buckets."""

        mapping = {
            "therapists": "therapists",
            "services": "services",
            "gallery": "gallery",
            "logo": "logo",
            "background": "background",
            "blog": "blog",
            "hero": "hero",
        }

        bucket = mapping.get(folder)

        if not bucket:
            raise ValueError(
                f"Unknown upload folder '{folder}'. "
                f"Allowed folders: {', '.join(mapping.keys())}"
            )

        return bucket

    # ============================================================
    # DEBUG / CONNECTION TEST
    # ============================================================

    @staticmethod
    def debug_connection() -> dict:
        """
        Test communication with Supabase Storage.

        This does NOT upload anything.
        """

        try:
            supabase_url = SupabaseStorage._get_supabase_url()
            key = SupabaseStorage._get_api_key()

            parsed = urlparse(supabase_url)
            hostname = parsed.hostname

            storage_url = f"{supabase_url}/storage/v1/bucket"

            current_app.logger.info("=" * 60)
            current_app.logger.info("SUPABASE STORAGE DEBUG")
            current_app.logger.info("=" * 60)
            current_app.logger.info(
                f"Supabase URL: {supabase_url}"
            )
            current_app.logger.info(
                f"Supabase hostname: {hostname}"
            )
            current_app.logger.info(
                f"Service key configured: {'YES' if key else 'NO'}"
            )
            current_app.logger.info(
                f"Testing endpoint: {storage_url}"
            )

            response = requests.get(
                storage_url,
                headers={
                    "Authorization": f"Bearer {key}",
                    "apikey": key,
                },
                timeout=20,
            )

            current_app.logger.info(
                f"Storage response status: {response.status_code}"
            )

            current_app.logger.info(
                f"Storage response body: {response.text[:1000]}"
            )

            current_app.logger.info("=" * 60)

            return {
                "success": response.ok,
                "status_code": response.status_code,
                "url": supabase_url,
                "hostname": hostname,
                "response": response.text[:1000],
            }

        except requests.exceptions.ConnectionError as e:
            current_app.logger.exception(
                "SUPABASE STORAGE CONNECTION ERROR"
            )

            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
            }

        except requests.exceptions.Timeout as e:
            current_app.logger.exception(
                "SUPABASE STORAGE TIMEOUT"
            )

            return {
                "success": False,
                "error": f"Timeout: {str(e)}",
            }

        except Exception as e:
            current_app.logger.exception(
                "SUPABASE STORAGE DEBUG ERROR"
            )

            return {
                "success": False,
                "error": str(e),
            }

    # ============================================================
    # UPLOAD
    # ============================================================

    @staticmethod
    def upload_file(file, folder: str, filename: str) -> dict:
        """
        Upload a file to Supabase Storage.
        """

        try:
            # ----------------------------------------------------
            # Validate configuration
            # ----------------------------------------------------

            supabase_url = SupabaseStorage._get_supabase_url()

            bucket = SupabaseStorage._get_bucket_for_folder(folder)

            # ----------------------------------------------------
            # Validate file
            # ----------------------------------------------------

            if not file:
                return {
                    "success": False,
                    "error": "No file object provided",
                }

            if not filename:
                return {
                    "success": False,
                    "error": "No filename provided",
                }

            # ----------------------------------------------------
            # Read file
            # ----------------------------------------------------

            file.seek(0)

            file_content = file.read()

            if not file_content:
                return {
                    "success": False,
                    "error": "Uploaded file is empty",
                }

            file_size = len(file_content)

            # ----------------------------------------------------
            # Content type
            # ----------------------------------------------------

            content_type = (
                getattr(file, "content_type", None)
                or mimetypes.guess_type(filename)[0]
                or "application/octet-stream"
            )

            # ----------------------------------------------------
            # Safely encode filename
            # ----------------------------------------------------

            safe_filename = quote(
                filename,
                safe="/"
            )

            # ----------------------------------------------------
            # Storage API endpoint
            # ----------------------------------------------------

            url = (
                f"{supabase_url}"
                f"/storage/v1/object/"
                f"{bucket}/"
                f"{safe_filename}"
            )

            headers = SupabaseStorage._get_headers(
                content_type
            )

            # ----------------------------------------------------
            # DEBUG LOGGING
            # ----------------------------------------------------

            current_app.logger.info("=" * 60)
            current_app.logger.info("SUPABASE STORAGE UPLOAD")
            current_app.logger.info("=" * 60)

            current_app.logger.info(
                f"Supabase URL: {supabase_url}"
            )

            current_app.logger.info(
                f"Bucket: {bucket}"
            )

            current_app.logger.info(
                f"Filename: {filename}"
            )

            current_app.logger.info(
                f"Encoded filename: {safe_filename}"
            )

            current_app.logger.info(
                f"Content-Type: {content_type}"
            )

            current_app.logger.info(
                f"File size: {file_size} bytes"
            )

            current_app.logger.info(
                f"Upload endpoint: {url}"
            )

            current_app.logger.info(
                "Authorization header: PRESENT"
            )

            current_app.logger.info(
                "API key header: PRESENT"
            )

            current_app.logger.info(
                "Sending request to Supabase..."
            )

            # ----------------------------------------------------
            # ACTUAL UPLOAD
            # ----------------------------------------------------

            response = requests.post(
                url,
                headers=headers,
                data=file_content,
                timeout=60,
            )

            # ----------------------------------------------------
            # RESPONSE DEBUG
            # ----------------------------------------------------

            current_app.logger.info(
                f"Supabase HTTP status: {response.status_code}"
            )

            current_app.logger.info(
                f"Supabase response headers: "
                f"{dict(response.headers)}"
            )

            current_app.logger.info(
                f"Supabase response body: "
                f"{response.text[:2000]}"
            )

            current_app.logger.info("=" * 60)

            # ----------------------------------------------------
            # SUCCESS
            # ----------------------------------------------------

            if response.status_code in (200, 201):

                public_url = (
                    f"{supabase_url}"
                    f"/storage/v1/object/public/"
                    f"{bucket}/"
                    f"{safe_filename}"
                )

                current_app.logger.info(
                    "✅ SUPABASE UPLOAD SUCCESSFUL"
                )

                current_app.logger.info(
                    f"Public URL: {public_url}"
                )

                return {
                    "success": True,
                    "url": public_url,
                    "size": file_size,
                    "bucket": bucket,
                    "filename": filename,
                }

            # ----------------------------------------------------
            # FAILURE
            # ----------------------------------------------------

            error_message = response.text

            try:
                error_data = response.json()

                if isinstance(error_data, dict):

                    error_message = (
                        error_data.get("message")
                        or error_data.get("error")
                        or error_data.get("statusCode")
                        or error_message
                    )

            except ValueError:
                pass

            current_app.logger.error(
                "❌ SUPABASE UPLOAD FAILED"
            )

            current_app.logger.error(
                f"HTTP status: {response.status_code}"
            )

            current_app.logger.error(
                f"Error: {error_message}"
            )

            return {
                "success": False,
                "error": (
                    f"Supabase Storage upload failed "
                    f"({response.status_code}): "
                    f"{error_message}"
                ),
                "status_code": response.status_code,
            }

        # --------------------------------------------------------
        # NETWORK ERRORS
        # --------------------------------------------------------

        except requests.exceptions.ConnectionError as e:

            current_app.logger.exception(
                "❌ SUPABASE CONNECTION ERROR"
            )

            return {
                "success": False,
                "error": (
                    f"Cannot connect to Supabase Storage: {str(e)}"
                ),
            }

        except requests.exceptions.Timeout as e:

            current_app.logger.exception(
                "❌ SUPABASE STORAGE TIMEOUT"
            )

            return {
                "success": False,
                "error": (
                    f"Supabase Storage request timed out: {str(e)}"
                ),
            }

        except requests.exceptions.RequestException as e:

            current_app.logger.exception(
                "❌ SUPABASE REQUEST ERROR"
            )

            return {
                "success": False,
                "error": (
                    f"Supabase request error: {str(e)}"
                ),
            }

        except Exception as e:

            current_app.logger.exception(
                "❌ SUPABASE STORAGE UNEXPECTED ERROR"
            )

            return {
                "success": False,
                "error": str(e),
            }

    # ============================================================
    # DELETE
    # ============================================================

    @staticmethod
    def delete_file(file_url: str) -> dict:
        """Delete a file from Supabase Storage."""

        try:

            supabase_url = (
                SupabaseStorage
                ._get_supabase_url()
            )

            if not file_url:
                return {
                    "success": True,
                    "skipped": True,
                }

            if not file_url.startswith(
                supabase_url
            ):
                current_app.logger.warning(
                    f"Skipping non-Supabase URL: {file_url}"
                )

                return {
                    "success": True,
                    "skipped": True,
                }

            prefix = (
                f"{supabase_url}"
                f"/storage/v1/object/public/"
            )

            if not file_url.startswith(prefix):
                return {
                    "success": True,
                    "skipped": True,
                }

            bucket_path = file_url[len(prefix):]

            parts = bucket_path.split("/", 1)

            if len(parts) != 2:
                return {
                    "success": True,
                    "skipped": True,
                }

            bucket, path = parts

            url = (
                f"{supabase_url}"
                f"/storage/v1/object/"
                f"{bucket}/"
                f"{quote(path, safe='/')}"
            )

            headers = SupabaseStorage._get_headers()

            current_app.logger.info(
                f"🗑️ Deleting Supabase file: {url}"
            )

            response = requests.delete(
                url,
                headers=headers,
                timeout=30,
            )

            current_app.logger.info(
                f"Delete response: {response.status_code}"
            )

            if response.status_code in (200, 204):

                current_app.logger.info(
                    "✅ Supabase file deleted"
                )

                return {
                    "success": True
                }

            current_app.logger.warning(
                f"Delete warning: "
                f"{response.status_code} "
                f"{response.text[:1000]}"
            )

            return {
                "success": True,
                "warn": True,
                "status_code": response.status_code,
            }

        except Exception as e:

            current_app.logger.exception(
                "❌ Supabase delete error"
            )

            return {
                "success": True,
                "warn": True,
                "error": str(e),
            }