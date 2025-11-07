from typing import Optional
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from ninja import Router, Schema, PatchDict

from users.services import (
    create_user_service,
    get_current_user_service,
    get_company_profile_service,
    update_profile_service
) 
from users.schema import (CompanyResponseSchema, UserCreateInput, UserUpdateInput, UserResponseOutput)
from config.responses import (SuccessResponseSchema, NotFoundError, ErrorCode)
from config.dependencies import authenticate_user

User = get_user_model()
router = Router(tags=["users"])



@router.post(
    "/register", 
    response={
        201: SuccessResponseSchema[UserResponseOutput],
        # 500: ErrorResponseSchema[None],
    }, 
    summary="Register a new user"
)
def register_user(request, payload: UserCreateInput):
    """
    Handles user registration by calling the UserService.
    Will raise ConflictError if the email already exists.
    """
    print(payload.email)
    user = create_user_service(payload)

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
    auth_user = request.auth
    
    current_user = get_current_user_service(id=str(auth_user.id))
        
    return SuccessResponseSchema[UserResponseOutput](
        status=ErrorCode.SUCCESS.value,
        message="Record retrieved successfully",
        data=current_user
    )

@router.patch(
    "/profile",
    response={200: SuccessResponseSchema[UserResponseOutput]},
    auth=authenticate_user,
    summary="Update user profile"
)
def update_user_profile(request, payload: PatchDict[UserUpdateInput]):
    """
    Updates the user profile 
    """
    auth_user = request.auth 
    updated_user = update_profile_service(str(auth_user.id), payload)
    
    return SuccessResponseSchema[UserResponseOutput](
        status=ErrorCode.SUCCESS.value,
        message="User updated successfully",
        data=update_user
    )


@router.get(
    "/company",
    response={200: SuccessResponseSchema[CompanyResponseSchema]},
    auth=authenticate_user,
    summary="Get company profile for user"
)
def get_company_profile(request):
    """
    Get company details by authenticated user
    """
    auth_user = request.auth
    company_profile = get_company_profile_service(str(auth_user.id))

    return SuccessResponseSchema[CompanyResponseSchema](
        status=ErrorCode.SUCCESS.value,
        message="Records retrieved successfully",
        data=company_profile
    )