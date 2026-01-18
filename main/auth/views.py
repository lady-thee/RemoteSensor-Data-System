from typing import Any, Dict

from ninja import Router, Schema

from config.responses import (
    SuccessResponseSchema, 
    ErrorCode, 
    ErrorResponseSchema,
    NotFoundError,
    InternalServerError
)
from auth.services import (
    authenicate_service,
    refresh_access_tokens_service,
    change_user_password_service,
    verify_account_service,
    generate_reset_password_code_service,
    reset_password_service
) 
from auth.schema import (
    LoginRequest, 
    RefreshRequest, 
    AccessTokenPayload,
    ResetPasswordRequest,
    TokenPairPayload,
    ActivateUserRequest,
    ResetPasswordTokenResponse,
    ResetPasswordTokenSchema,
    ChangePasswordRequest,
)
from config.dependencies import authenticate_user
from users.schema import UserResponseOutput

router = Router(tags=["auth"])

@router.post(
    "/login", 
    response={200: SuccessResponseSchema[TokenPairPayload]}, 
    summary="Login User"
)
def login(request, payload: LoginRequest):
    """
    Authenticates user and calls the service to generate a new JWT pair.
    Raises UnauthorizedError on invalid credentials (handled by the service).
    """
    
    tokens = authenicate_service(**payload.model_dump())

    # token_data = TokenPairPayload.model_validate(tokens)
    
    return SuccessResponseSchema[TokenPairPayload](
        status=ErrorCode.SUCCESS.value,
        message="Login successful.", 
        data=tokens
    )


@router.post(
    "/activate",
    response={
        200: SuccessResponseSchema[None]
    },
    summary="Activate User Email"
)
def activate_user(request, payload: ActivateUserRequest):
    """
    Verify user account
    """

    verify_account_service(**payload.model_dump())

    return SuccessResponseSchema[None](
        status=ErrorCode.SUCCESS.value,
        message="Email address successfully activated."
    )


@router.post(
    "/token-refresh", 
    response={200: SuccessResponseSchema[AccessTokenPayload]},
    summary="Refresh Access Token"
)
def refresh_token(request, payload: RefreshRequest):
    """
    Refreshes the access token using a valid refresh token.
    Raises UnauthorizedError on invalid or expired refresh token (handled by the service).
    """
    
    tokens = refresh_access_tokens_service(**payload.model_dump())
    
    # token_data = AccessTokenPayload.model_validate(tokens)
    
    return SuccessResponseSchema[AccessTokenPayload](
        status=ErrorCode.SUCCESS.value,
        message="Refresh tokens successful.", 
        data=tokens
    )


@router.patch(
    "/send-password-token",
    response={200: SuccessResponseSchema[ResetPasswordTokenResponse]},
    summary="Generates Password Code"
)
def generate_reset_password_code(request, payload: ResetPasswordTokenSchema):
    """
    Generates and send reset password token to user
    """
    response = generate_reset_password_code_service(**payload.model_dump())

    return SuccessResponseSchema[ResetPasswordTokenResponse](
        status=ErrorCode.SUCCESS.value,
        message="Password link sent to email",
        data=response
    )


@router.patch(
    "/change-password",
    response={200: SuccessResponseSchema[UserResponseOutput]},
    auth=authenticate_user,
    summary="Update User Password"
)
def change_password(request, payload: ChangePasswordRequest):
    """
    Updates/Changes user password
    """
    response = change_user_password_service(payload)
    
    return SuccessResponseSchema[UserResponseOutput](
        status=ErrorCode.SUCCESS.value,
        message="Password succcessfully changed",
        data=payload
    )


@router.patch(
    "/reset-password",
    response={200: SuccessResponseSchema[UserResponseOutput]},
    summary="Reset User Pasword"
)
def reset_password(request, payload: ResetPasswordRequest):
    """
    When user forgets password, this URL will reset password
    """
    response = reset_password_service(payload)

    return SuccessResponseSchema[UserResponseOutput](
        status=ErrorCode.SUCCESS.value,
        message="Password succcessfully reset",
        data=response
    )