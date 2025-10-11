import logging
from typing import Optional
from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError, IntegrityError
from config.responses import (
    ConflictError, 
    SuccessResponseSchema, 
    NotFoundError, 
    InternalServerError
)
from users.schema import UserResponseOutput, UserCreateInput

logger = logging.getLogger(__name__)
User = get_user_model()

class UserService:
    """
    Service layer for all user-related business logic
    """
    
    @transaction.atomic
    def create_user(
        self, 
        email: str, 
        username: str, 
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        residence: Optional[str] = None,
    ) -> UserResponseOutput:
        """
        Creates a new user using the custom UserManager.
        
        Args:
            email: The unique email address.
            password: The plain text password.
            fullname: The user's full name.
            
        Returns:
            The newly created User object.
        
         Raises:
            ConflictError: If a user with the given email already exists or invalid role is submitted.
        """

        logger.info(f"Attempting to create user with email={email}")

        # check duplicate
        if User.objects.filter(email=email).exists():
            logger.warning(f"User creation failed — email already exists: {email}")
            raise ConflictError(message="A user with that email already exists.")

        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                city=city,
                state=state,
                country=country,
                residence=residence,
            )
            logger.info(f"User account created successfully for {email}")
            return UserResponseOutput.model_validate(user)
        except IntegrityError as e:
            logger.exception(f"Database integrity error while creating user {email}: {e}")
            raise ConflictError(message="Database integrity error while creating user.")
        except DatabaseError as e:
            logger.exception(f"Database error while creating user {email}: {e}")
            raise InternalServerError(message="Database operation failed.")
        except Exception as e:
            logger.exception(f"Unexpected error while creating user {email}: {e}")
            raise InternalServerError(message="Unexpected error occurred during user creation.")


    @staticmethod
    def get_current_user(id: str):
        """
        Fetches the profile of the user if authenticated.

        Args:
            id: The user's UUID.

        Returns:
            The User object.

        Raises:
            NotFoundError: If the user does not exist.
        """
        logger.debug(f"Fetching current user with id={id}")
        try:
            user = User.objects.get(id=id)
            logger.info(f"User retrieved successfully: {user.email}")
            return user
        except User.DoesNotExist:
            logger.warning(f"User with id={id} not found")
            raise NotFoundError(message=f"User with id '{id}' not found.")
        except Exception as e:
            logger.exception(f"Unexpected error fetching user id={id}: {e}")
            raise NotFoundError(message=f"Unexpected error fetching user (Error: {e})")


user_service = UserService()