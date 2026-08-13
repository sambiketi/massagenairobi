import re
import json
from datetime import datetime, timedelta
from flask import current_app

class Helpers:
    """Utility helper functions"""
    
    @staticmethod
    def format_currency(amount):
        """Format currency in KES"""
        return f"KES {amount:,.0f}"
    
    @staticmethod
    def format_date(date_obj, format='%Y-%m-%d'):
        """Format date object to string"""
        if date_obj:
            return date_obj.strftime(format)
        return None
    
    @staticmethod
    def format_datetime(dt_obj, format='%Y-%m-%d %H:%M'):
        """Format datetime object to string"""
        if dt_obj:
            return dt_obj.strftime(format)
        return None
    
    @staticmethod
    def get_week_dates():
        """Get dates for current week (Monday to Sunday)"""
        today = datetime.utcnow().date()
        monday = today - timedelta(days=today.weekday())
        return [monday + timedelta(days=i) for i in range(7)]
    
    @staticmethod
    def slugify(text):
        """Convert text to URL-friendly slug"""
        text = re.sub(r'[^\w\s-]', '', text).strip().lower()
        return re.sub(r'[-\s]+', '-', text)
    
    @staticmethod
    def truncate_text(text, length=100, suffix='...'):
        """Truncate text to specified length"""
        if not text:
            return ''
        if len(text) <= length:
            return text
        return text[:length] + suffix
    
    @staticmethod
    def safe_json_loads(json_string):
        """Safely parse JSON string"""
        try:
            return json.loads(json_string) if json_string else {}
        except json.JSONDecodeError:
            return {}
    
    @staticmethod
    def get_client_ip():
        """Get client IP address from request"""
        from flask import request
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        return request.remote_addr
    
    @staticmethod
    def generate_reference(prefix='REF', length=8):
        """Generate unique reference number"""
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        random_part = ''.join(random.choices(chars, k=length))
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        return f"{prefix}{timestamp}{random_part}"