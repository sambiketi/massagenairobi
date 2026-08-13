import re
from datetime import datetime

class Validators:
    """Validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) if email else True
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (Kenyan format)"""
        # Remove any spaces or special characters
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check format: 2547XXXXXXXX or 07XXXXXXXX or 7XXXXXXXX
        pattern = r'^(2547\d{8}|07\d{8}|7\d{8})$'
        return bool(re.match(pattern, phone)) if phone else False
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_time(time_str: str) -> bool:
        """Validate time format HH:MM"""
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_mpesa_code(code: str) -> bool:
        """Validate M-Pesa transaction code format"""
        if not code:
            return True  # Optional field
        # M-Pesa codes are usually alphanumeric, 5-15 characters
        return bool(re.match(r'^[A-Z0-9]{5,15}$', code.upper()))
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        if not text:
            return ''
        # Remove any potentially dangerous characters
        return re.sub(r'[<>{}]', '', text).strip()