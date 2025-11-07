from uuid import UUID
from ninja import Schema, ModelSchema
from typing import List, Optional, Dict, Any
from users.models import (AccountStatus, Account, AccountTypes, CompanyProfile, SubscriptionPlan)

class MetadataSchema(Schema):
    timezone: Optional[str] = None
    logo_url: Optional[str] = None
    iot_platform_id: Optional[str] = None


class SettingsSchema(Schema):
    theme: Optional[str] = "light"
    notifications_enabled: Optional[bool] = True
    language: Optional[str] = "en"
    data_refresh_interval: Optional[int] = 15


class BillingInfoSchema(Schema):
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    billing_address: Optional[str] = None
    next_billing_date: Optional[str] = None


class UserCreateInput(Schema):
    # authentication
    email: str
    password: str
    account_type: str 

    # profile info
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

    # location
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    residence: Optional[str] = None
    postal_code: Optional[str] = None

    # company-like info
    company_name: Optional[str] = None
    description: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    registration_number: Optional[str] = None

    # subscription & account state
    subscription_plan: Optional[str] = SubscriptionPlan.FREE
    status: Optional[str] = AccountStatus.ACTIVE

    # JSON fields
    metadata: Optional[MetadataSchema] = MetadataSchema()
    settings: Optional[SettingsSchema] = SettingsSchema()


class UserUpdateInput(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    residence: Optional[str] = None
    postal_code: Optional[str] = None

    company_name: Optional[str] = None
    description: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    registration_number: Optional[str] = None

    subscription_plan: Optional[str] = None
    status: Optional[str] = None

    metadata: Optional[MetadataSchema] = None
    settings: Optional[SettingsSchema] = None
    billing_info: Optional[BillingInfoSchema] = None


class UserResponseOutput(ModelSchema):
    id: UUID 
    class Meta:
        model = Account 
        exclude = ['password', 'last_login', 'user_permissions']


class CompanyResponseSchema(ModelSchema):
    id: UUID 
    class Meta:
        model = CompanyProfile
        fields = "__all__"