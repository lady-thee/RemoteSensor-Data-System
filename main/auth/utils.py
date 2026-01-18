import random
import jwt
from datetime import datetime, timezone, timedelta
from django.conf import settings
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model

User = get_user_model()

ACCESS_TOKEN_LIFETIME_DAYS = settings.ACCESS_TOKEN_LIFETIME_DAYS
REFRESH_TOKEN_LIFETIME_DAYS = settings.REFRESH_TOKEN_LIFETIME_DAYS
ALGORITHM = settings.ALGORITHM


class JWTUtils:
    """
    Utility class for generating, verifying, and refreshing JWT tokens.
    Uses settings.JWT_AUTH for configuration.
    """
    # --- Token Generation Methods ---

    @staticmethod
    def generate_access_token(user: User) -> str:
        """
        Generates an access token signed with user ID and email.
        """
        
        # Calculate expiration time
        expiration = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_LIFETIME_DAYS)

        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'token_type': 'access',
            'exp': expiration,
            'iat': datetime.now(timezone.utc),
        }

        return jwt.encode(
            payload, 
            settings.SECRET_KEY, 
            algorithm=ALGORITHM
        )

    @staticmethod
    def generate_refresh_token(user: User) -> str:
        """
        Generates a refresh token signed with user ID.
        """
        # Calculate expiration time
        expiration = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)

        payload = {
            'user_id': str(user.id),
            'token_type': 'refresh',
            'exp': expiration,
            'iat': datetime.now(timezone.utc),
        }

        return jwt.encode(
            payload, 
            settings.SECRET_KEY, 
            algorithm=ALGORITHM
        )

    # --- Verification Method ---

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verifies a token and returns its payload if valid.
        Returns None if verification fails (expired, invalid signature, etc.).
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=ALGORITHM
            )
            return payload
        except jwt.PyJWTError:
            return None

    # --- Refresh Method ---

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Uses a valid refresh token to generate a new access token.
        Returns a dict with {'access_token': '...'} or None on failure.
        """
        payload = JWTUtils.verify_token(refresh_token)

        if payload is None:
            return None # Invalid or expired refresh token

        # 1. Check if it's actually a refresh token
        if payload.get('token_type') != 'refresh':
            return None 
            
        # 2. Retrieve the user (optional, but good practice to ensure the user still exists)
        user_id = payload.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

        # 3. Generate a new access token
        new_access_token = JWTUtils.generate_access_token(user)

        return {
            'access_token': new_access_token
        }
    
    @staticmethod
    def generate_plain_token() -> str:
        return str(random.randint(100000, 999999))
    