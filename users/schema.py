from uuid import UUID
from django.contrib.auth.models import User
from ninja import Schema, ModelSchema
from typing import List, Optional

class UserCreateInput(Schema):
    email: str 
    username: str 
    password: str 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    residence: Optional[str] = None

    # model_config = {
    #     'from_attributes': True
    # }


class UserResponseOutput(ModelSchema):
    id: UUID 
    class Meta:
        model = User 
        exclude = ['password', 'last_login', 'user_permissions']