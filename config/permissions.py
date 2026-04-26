import pyotp
import os
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class HasValidTOTP(BasePermission):
    """
    Custom permission to verify the X-OTP header.
    """
    def has_permission(self, request, view):
        totp_secret = os.getenv('TOTP_SECRET')
        if not totp_secret:
            raise PermissionDenied("Server TOTP secret not configured.")
            
        totp = pyotp.TOTP(totp_secret, interval=15)
        user_otp = request.headers.get('X-OTP')
        
        if not user_otp or not totp.verify(user_otp):
            return False
            
        return True