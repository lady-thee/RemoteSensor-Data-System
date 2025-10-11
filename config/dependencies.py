import jwt
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.conf import settings
from config.responses import UnauthorizedError
from ninja.security import HttpBearer
from config.responses import ForbiddenError


def get_authenticated_user_from_token(token: str):
    """
    Decodes the JWT token, extracts the user ID, and returns the User object.
    
    Raises:
        UnauthorizedError: If the token is invalid, expired, or user not found.
    """
    User = get_user_model()
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ "HS256"])
        
        user_id = payload.get('user_id') 
        
        if not user_id:
            raise UnauthorizedError("Invalid token payload: user_id missing.")
            
        user = User.objects.get(id=user_id, is_active=True)
        
        print(user)
        return user
        
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("JWT token has expired.")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid JWT token.")
    except User.DoesNotExist:
        raise UnauthorizedError("User associated with token not found.")
    except Exception as e:
        raise UnauthorizedError(f"Authentication failed: {e}")


class UserJWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        if not token:
            raise UnauthorizedError("Authentication token not provided.")
            
        user = get_authenticated_user_from_token(token)
        
        return user
    

authenticate_user = UserJWTAuth()
