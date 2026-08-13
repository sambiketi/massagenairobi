import os
import json
import requests
import base64
from datetime import datetime
from flask import current_app
from typing import Dict, Any, Optional

class MpesaService:
    """Service for M-Pesa Daraja API integration"""
    
    @staticmethod
    def get_access_token() -> str:
        """Get M-Pesa access token from Safaricom API"""
        consumer_key = current_app.config.get('MPESA_CONSUMER_KEY')
        consumer_secret = current_app.config.get('MPESA_CONSUMER_SECRET')
        
        # Check if credentials are configured
        if not consumer_key or not consumer_secret:
            # Return dummy token for development/testing
            return "dummy_access_token_development"
        
        try:
            url = "https://sandbox.safaricom.co.ke/oauth/v1/generate"
            params = {
                "grant_type": "client_credentials"
            }
            auth = (consumer_key, consumer_secret)
            
            response = requests.get(url, params=params, auth=auth, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('access_token')
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"M-Pesa access token error: {str(e)}")
            return None
    
    @staticmethod
    def stk_push(phone_number: str, amount: int, account_reference: str, 
                 transaction_desc: str = "Massage Payment") -> Dict[str, Any]:
        """
        Initiate STK Push transaction to customer's phone
        
        Args:
            phone_number: Customer phone number (format: 2547XXXXXXXX)
            amount: Amount in KES
            account_reference: Your account reference
            transaction_desc: Description of transaction
        
        Returns:
            Dictionary with transaction details
        """
        # Check if M-Pesa is configured
        shortcode = current_app.config.get('MPESA_SHORTCODE')
        passkey = current_app.config.get('MPESA_PASSKEY')
        consumer_key = current_app.config.get('MPESA_CONSUMER_KEY')
        consumer_secret = current_app.config.get('MPESA_CONSUMER_SECRET')
        
        if not all([shortcode, passkey, consumer_key, consumer_secret]):
            # Return simulated response for development
            return {
                'success': True,
                'checkout_request_id': f'CHECKOUT_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'response_code': '0',
                'response_description': 'Success. Request accepted for processing (Simulated)',
                'customer_message': 'Payment request sent to your phone',
                'simulated': True
            }
        
        try:
            # Get access token
            access_token = MpesaService.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': 'Failed to get M-Pesa access token'
                }
            
            # Format phone number
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # Prepare STK Push request
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"{shortcode}{passkey}{timestamp}".encode()
            ).decode()
            
            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            
            payload = {
                "BusinessShortCode": shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": current_app.config.get('MPESA_CALLBACK_URL', 'https://your-domain.com/mpesa/callback'),
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': True,
                'checkout_request_id': result.get('CheckoutRequestID'),
                'response_code': result.get('ResponseCode'),
                'response_description': result.get('ResponseDescription'),
                'customer_message': result.get('CustomerMessage'),
                'simulated': False
            }
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"M-Pesa STK Push error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def query_status(checkout_request_id: str) -> Dict[str, Any]:
        """
        Query the status of an STK Push transaction
        
        Args:
            checkout_request_id: The checkout request ID from stk_push
        
        Returns:
            Transaction status details
        """
        shortcode = current_app.config.get('MPESA_SHORTCODE')
        passkey = current_app.config.get('MPESA_PASSKEY')
        
        if not shortcode or not passkey:
            # Simulated response for development
            return {
                'success': True,
                'result_code': '0',
                'result_desc': 'The service request is processed successfully (Simulated)',
                'simulated': True
            }
        
        try:
            access_token = MpesaService.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': 'Failed to get M-Pesa access token'
                }
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"{shortcode}{passkey}{timestamp}".encode()
            ).decode()
            
            url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
            
            payload = {
                "BusinessShortCode": shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': True,
                'result_code': result.get('ResultCode'),
                'result_desc': result.get('ResultDesc'),
                'amount': result.get('Amount'),
                'mpesa_receipt': result.get('MpesaReceiptNumber'),
                'transaction_date': result.get('TransactionDate'),
                'phone_number': result.get('PhoneNumber'),
                'simulated': False
            }
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"M-Pesa query status error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def verify_payment(mpesa_code: str) -> Dict[str, Any]:
        """
        Verify a payment using M-Pesa transaction code
        This is a simplified verification for the Till approach
        
        Args:
            mpesa_code: The M-Pesa transaction code entered by customer
        
        Returns:
            Verification result
        """
        # For the Till approach, we just validate the format
        # In production, you would call Safaricom's API to verify
        if not mpesa_code or len(mpesa_code) < 5:
            return {
                'success': False,
                'error': 'Invalid M-Pesa transaction code'
            }
        
        # Simulate verification
        return {
            'success': True,
            'transaction_status': 'Completed',
            'mpesa_code': mpesa_code,
            'verified_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_till_payment_instructions(till_number: str, amount: int, 
                                          account: str = 'Massage') -> str:
        """
        Generate M-Pesa Till payment instructions for the customer
        
        Args:
            till_number: The Till/Buy Goods number
            amount: Amount in KES
            account: Account reference
        
        Returns:
            Formatted payment instructions
        """
        return f"""
M-PESA TILL PAYMENT INSTRUCTIONS
{'=' * 30}

1. Go to M-PESA menu on your phone
2. Select 'Lipa na M-PESA'
3. Select 'Buy Goods and Services'
4. Enter Till Number: {till_number}
5. Enter Amount: KES {amount:,}
6. Enter Account: {account}
7. Enter your M-PESA PIN
8. Confirm and complete payment

After payment, enter the transaction code in the booking form.
        """.strip()
    
    @staticmethod
    def generate_stk_push_message(phone: str, amount: int, account: str) -> str:
        """
        Generate message for STK Push request
        
        Args:
            phone: Customer phone number
            amount: Amount in KES
            account: Account reference
        
        Returns:
            Formatted STK Push message
        """
        return f"""
STK PUSH PAYMENT REQUEST
{'=' * 30}

A payment request of KES {amount:,} has been sent to:
{phone}

Please check your phone for the M-PESA PIN prompt.
Enter your PIN to complete the payment.

Reference: {account}
        """.strip()