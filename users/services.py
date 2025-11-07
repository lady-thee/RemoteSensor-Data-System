import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction, DatabaseError, IntegrityError
from django.utils import timezone
from users.models import (AccountStatus, CompanyProfile, AccountTypes, SubscriptionPlan)
from config.responses import (
    ConflictError, 
    SuccessResponseSchema, 
    NotFoundError, 
    InternalServerError
)
from users.schema import (
    UserResponseOutput, 
    UserCreateInput, 
    UserUpdateInput,
    CompanyResponseSchema
)
from auth.utils import JWTUtils

logger = logging.getLogger(__name__)
User = get_user_model()


@transaction.atomic
def create_user_service(data: UserCreateInput) -> UserResponseOutput:
    """
    Creates a new user using the custom UserManager.
    """
    payload = data.model_dump()
    email = payload.get("email")
    logger.info(f"Attempting to create user with email={email}")
    # check duplicate
    if User.objects.filter(email=email).exists():
        logger.warning(f"User creation failed — email already exists: {email}")
        raise ConflictError(message="A user with that email already exists.")

    if data.account_type == AccountTypes.INDIVIDUAL:
        logger.info("Creating INDIVIDUAL Account")
    
    if data.account_type == AccountTypes.COMPANY:
        logger.info("Creating COMPANY Account")
    
    try:
        # Creating token
        token = JWTUtils.generate_plain_token()
        print(token)
        salt = bcrypt.gensalt()
        hashed_token = bcrypt.hashpw(token.encode(), salt)

        logger.info("[Users.Token] Activation code generated")
        # print(token, hashed_token)

        current_time = timezone.now() + timedelta(hours=1)

        # Filter fields depending on account type
        if data.account_type == AccountTypes.INDIVIDUAL:
            allowed_fields = {
                "email", "username", "password", "account_type", "first_name",
                "last_name", "phone", "bio", "city", "state", "country",
                "residence", "postal_code", "subscription_plan", "status",
                "metadata", "settings", "billing_info"
            }

        elif data.account_type == AccountTypes.COMPANY:
            allowed_fields = {
                "email", "username", "password", "account_type", "company_name",
                "description", "address_line1", "address_line2", "website_url",
                "industry", "registration_number", "phone", "city", "state",
                "country", "postal_code", "subscription_plan", "status",
                "metadata", "settings", "billing_info"
            }
        else:
            raise ValidationError("Invalid account type provided.")

        # Keep only fields that match model attributes
        filtered_data = {k: v for k, v in payload.items() if k in allowed_fields}

        # Create the user
        user = User.objects.create_user(
            activation_code=hashed_token.decode(),
            activation_code_created_at=current_time,
            **filtered_data,
        )

        logger.info(f"User account created successfully for {email}")

        return UserResponseOutput.model_validate(user)
    except ValidationError as e:
        logger.exception(f"Error during tokenization: {e}")
        raise ConflictError(f"There was a problem during creation, please try again later")
    except IntegrityError as e:
        logger.exception(f"Database integrity error while creating user {email}: {e}")
        raise ConflictError(message="Database integrity error while creating user.")
    except DatabaseError as e:
        logger.exception(f"Database error while creating user {email}: {e}")
        raise InternalServerError(message="Database operation failed.")
    # except Exception as e:
    #     logger.exception(f"Unexpected error while creating user {email}: {e}")
    #     raise InternalServerError(message="Unexpected error occurred during user creation.")


def get_current_user_service(id: str) -> UserResponseOutput:
    """
    Fetches the profile of the user if authenticated.

    Args:
        id: The user's UUID.

    Returns:
        The User object.

    Raises:
        NotFoundError: If the user does not exist.
    """
    logger.info(f"Fetching current user with id={id}")
    try:
        user = User.objects.get(id=id)
        logger.info(f"User retrieved successfully: {user.email}")
        return UserResponseOutput.model_validate(user)
    except User.DoesNotExist:
        logger.warning(f"User with id={id} not found")
        raise NotFoundError(message=f"User with id '{id}' not found.")
    except Exception as e:
        logger.exception(f"Unexpected error fetching user id={id}: {e}")
        raise InternalServerError(message=f"Unexpected error fetching user (Error: {e})")


@transaction.atomic()
def update_profile_service(id: str, data: UserUpdateInput) -> UserResponseOutput:
    """
    Updates the profile of the user, minus password. 

    Args:
        id: The user's UUID
    
    Returns: 
        The User object with updated fields.
    """
    logger.info(f"Updating the user profile with id={id}")

    try:
        user = User.objects.get(id=id)
        logger.info(f"User retrieved successfully: {user.email}") 
        
        # Attempting to update user
        for attr, value in data.items():
            setattr(user, attr, value)
        
        user.save()
        return UserResponseOutput.model_validate(user)
    except User.DoesNotExist:
        logger.warning(f"User with id={id} not found")
        raise NotFoundError(message=f"User with id '{id}' not found.")
    except Exception as e:
        logger.exception(f"Unexpected error fetching user id={id}: {e}")
        raise InternalServerError(message=f"Unexpected error fetching user (Error: {e})")


def get_company_profile_service(account_id) -> CompanyResponseSchema:
    """
    Get company for authenticated user
    """
    logger.info(f"Retrieving Company details for User: {account_id}")
    try:
        company = CompanyProfile.objects.get(account=account_id)
        logger.info(f"Company Profile retrieved successfully: {company.id}")
        return CompanyResponseSchema.model_validate(company)
    except CompanyProfile.DoesNotExist:
        logger.warning(f"Company belonging to account_id={account_id} not found")
        raise NotFoundError(message=f"Company belonging to account_id={account_id} not found")
    except Exception as e:
        logger.exception(f"Unexpected error fetching company with account id={account_id}: {e}")
        raise InternalServerError(message=f"Unexpected error fetching user (Error: {e})")


