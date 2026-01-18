from ninja import Router, Schema
from typing import Optional


class LoginRequest(Schema):
    """Schema for user credentials during login."""
    email: str
    password: str

class TokenPairPayload(Schema):
    """Schema for returning both access and refresh tokens."""
    access_token: str
    refresh_token: str

class RefreshRequest(Schema):
    """Schema for submitting a refresh token."""
    refresh_token: str

class AccessTokenPayload(Schema):
    """Schema for returning only the new access token."""
    access_token: str

# class ChangePasswordRequest(Schema):
#     old_password: str
#     new_password: str 

class ActivateUserRequest(Schema):
    token: str 
    email: str 

class ResetPasswordTokenSchema(Schema):
    email: str 

class ResetPasswordTokenResponse(Schema):
    status: str

class ChangePasswordRequest(ActivateUserRequest):
    old_password: str 
    new_password: str 

class ResetPasswordRequest(ActivateUserRequest):
    new_password: str