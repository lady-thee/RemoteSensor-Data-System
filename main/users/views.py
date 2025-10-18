from typing import Optional
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from ninja import Router, Schema

from users.services import user_service 
from users.schema import UserCreateInput, UserResponseOutput
from config.responses import SuccessResponseSchema, NotFoundError, ErrorCode
from config.dependencies import authenticate_user

User = get_user_model()
router = Router(tags=["users"])



@router.post(
    "/register", 
    response={201: SuccessResponseSchema[UserResponseOutput]}, 
    summary="Register a new user"
)
def register_user(request, payload: UserCreateInput):
    """
    Handles user registration by calling the UserService.
    Will raise ConflictError if the email already exists.
    """
    print(payload.email)
    user = user_service.create_user(
        **payload.model_dump()
    )

    return SuccessResponseSchema[UserResponseOutput](
        status_code=ErrorCode.SUCCESS.value,
        message="User successfully registered",
        data=user
    )


@router.get(
    "/me",
    response={200: SuccessResponseSchema[UserResponseOutput]},
    auth=authenticate_user,
    summary="Get the currently authenticated user's profile"
)
def get_current_user(request):
    """
    Fetches the profile of the authenticated user using the User object 
    attached by the JWT authenticator.
    """
    authenticated_user = request.auth
    
    current_user = user_service.get_current_user(id=str(authenticated_user.id))
        
    user_payload = UserPayload.model_validate(current_user)
    
    return SuccessResponseSchema[UserResponseOutput](
        status=ErrorCode.SUCCESS.value,
        message="Record retrieved successfully",
        data=user_payload
    )