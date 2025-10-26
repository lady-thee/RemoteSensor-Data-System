import bcrypt
import logging
from typing import Optional, Dict
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db import transaction, DatabaseError, IntegrityError
from django.utils import timezone

from auth.utils import JWTUtils
from auth.schema import (TokenPairPayload, AccessTokenPayload, ChangePasswordRequest, ResetPasswordTokenResponse, ResetPasswordRequest)
from users.schema import UserResponseOutput
from config.responses import (
    UnauthorizedError, 
    InvalidInputError, 
    ConflictError,
    NotFoundError,
    InternalServerError,
    BadRequestError
) 

logger = logging.getLogger(__name__)

User = get_user_model()


def authenicate_service(email: str, password: str) -> TokenPairPayload:
    """
    Authenticates the user and generates new access and refresh tokens.
    
    Raises:
        UnauthorizedError: If the credentials are invalid.
    """
    try:
        user = authenticate(email=email, password=password)
        
        if user is None:
            raise UnauthorizedError(message="Invalid email or password.")

        if not user.is_verified:
            raise UnauthorizedError(message="You have to verify account first")
        
        # print(user)
        access_token = JWTUtils.generate_access_token(user)
        refresh_token = JWTUtils.generate_refresh_token(user)

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    except User.DoesNotExist:
        logger.warning(f"User with email={email} not found")
        raise NotFoundError(message=f"User with email '{email}' not found.")
    except ValidationError  as e:
        logger.exception(f"Error authenticating user: {e}")
        raise BadRequestError(f"Could not authenticate user with email. Please try again later")


def refresh_access_tokens_service(refresh_token: str) -> AccessTokenPayload:
    """
    Takes a refresh token and returns a new access token.
    
    Raises:
        UnauthorizedError: If the refresh token is invalid or expired.
    """
    
    tokens = JWTUtils.refresh_access_token(refresh_token)
    
    if tokens is None:
        raise UnauthorizedError(message="Invalid or expired refresh token.")
        
    return AccessTokenPayload.model_validate(tokens)


@transaction.atomic
def verify_account_service(email: str, token: str) -> bool:
    """
    Verify user email
    """
    try:
        user = User.objects.get(email=email)
        if not user.activation_code:
            raise BadRequestError("No activation code found for this user.")
        
        if not user.is_activation_code_expired:
            raise BadRequestError("Activation code has expired. Please request a new one")
        
        if not bcrypt.checkpw(token.encode("utf-8"), user.activation_code.encode("utf-8")):
            raise InvalidInputError("Invalid or incorrect activation token.")
        
        user.is_verified = True 
        user.is_active = True
        user.activation_code = None
        user.save(update_fields=["is_verified", "activation_code", "is_active"])

        return True
    except User.DoesNotExist:
        logger.warning(f"User with email={email} not found")
        raise NotFoundError(message=f"User with email '{email}' not found.")
    except ValidationError as e:
        logger.exception(f"Validation error while verfiying email: {e}")
    # except Exception as e:
    #     logger.exception(f"Unexpected error verifying user email={email}: {e}")
    #     raise InternalServerError(message=f"Unexpected error verifying user (Error: {e})")

@transaction.atomic
def generate_reset_password_code_service(email: str) -> ResetPasswordTokenResponse:
    try:
        user = User.objects.get(email=email)
        reset_token = JWTUtils.generate_plain_token()
        print(reset_token)
        salt = bcrypt.gensalt()
        hashed_token = bcrypt.hashpw(reset_token.encode(), salt)

        user.reset_password_code = hashed_token.decode()
        user.reset_password_code_created_at = timezone.now()
        user.save(update_fields=["reset_password_code", "reset_password_code_created_at"])
        return ResetPasswordTokenResponse.model_validate(
            {
                "status": "PROCESSING"
            }
        )
    except ValidationError as e:
        logger.exception(f"Error during tokenization: {e}")
        raise ConflictError(f"There was a problem during creation, please try again later")
    except IntegrityError as e:
        logger.exception(f"Database integrity error while resetting password for user {email}: {e}")
        raise ConflictError(message="Database integrity error while resetting password")
    except DatabaseError as e:
        logger.exception(f"Database error while resetting password user password for {email}: {e}")
        raise InternalServerError(message="Database operation failed.") 


@transaction.atomic
def change_user_password_service(data: ChangePasswordRequest) -> UserResponseOutput:
    """
    Chnages password for user 
    """
    try:
        payload = data.model_dump()

        email = payload.get("email")
        token = payload.get("token")
        old_password = payload.get("old_password")
        new_password = payload.get("new_password")

        user = User.objects.get(email=email)
        
        logger.info("Validating Reset Token")

        # Check if token is valid
        if not user.reset_password_code:
            raise BadRequestError("No reset password code found for this user.")
        
        if not user.is_reset_password_token_expired:
            raise BadRequestError("Reset password code has expired. Please request a new one")
        
        logger.info("Decoding Reset Code")
        if not bcrypt.checkpw(token.encode("utf-8"), user.reset_password_code.encode("utf-8")):
            raise InvalidInputError("Invalid or incorrect reset token.")

        # Check password
        logger.info("Checking User Pasword")
        if not check_password(old_password, user.password):
            raise InvalidInputError("Old password is incorrect!")
        
        user.reset_password_code = None
        user.set_password(new_password)
        user.save(update_fields=["password", "reset_password_code"])

        logger.info("User password changed successfully")
        return UserResponseOutput.model_validate(user) 
    except User.DoesNotExist:
        logger.warning(f"User with email={email} not found")
        raise NotFoundError(message=f"User with email '{email}' not found.")
    except IntegrityError as e:
        logger.exception(f"Database integrity error while resetting password for user {email}: {e}")
        raise ConflictError(message="Database integrity error while resetting password")
    except DatabaseError as e:
        logger.exception(f"Database error while resetting password user password for {email}: {e}")
        raise InternalServerError(message="Database operation failed.") 


@transaction.atomic
def reset_password_service(data: ResetPasswordRequest) -> UserResponseOutput:
    """
    Resets password for user 
    """
    try:
        payload = data.model_dump()

        email = payload.get("email")
        token = payload.get("token")
        new_password = payload.get("new_password")

        user = User.objects.get(email=email)
        
        logger.info("Validating Reset Token")


        # Check if token is valid
        if not user.reset_password_code:
            raise BadRequestError("No reset password code found for this user.")
        
        if not user.is_reset_password_token_expired:
            raise BadRequestError("Reset password code has expired. Please request a new one")
        
        logger.info("Decoding Reset Code")
        if not bcrypt.checkpw(token.encode("utf-8"), user.reset_password_code.encode("utf-8")):
            raise InvalidInputError("Invalid or incorrect reset token.")

        # Check password
        logger.info("Checking User Pasword")
        if check_password(new_password, user.password):
            raise InvalidInputError("New password cannot be the same as the old password.")
        
        user.reset_password_code = None
        user.set_password(new_password)
        user.reset_password_code_created_at = timezone.now()
        user.save(update_fields=["password", "reset_password_code", "reset_password_code_created_at"])

        logger.info("User password changed successfully")
        return UserResponseOutput.model_validate(user)
    except User.DoesNotExist:
        logger.warning(f"User with email={email} not found")
        raise NotFoundError(message=f"User with email '{email}' not found.")
    except IntegrityError as e:
        logger.exception(f"Database integrity error while resetting password for user {email}: {e}")
        raise ConflictError(message="Database integrity error while resetting password")
    except DatabaseError as e:
        logger.exception(f"Database error while resetting password user password for {email}: {e}")
        raise InternalServerError(message="Database operation failed.") 
