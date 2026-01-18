from uuid import UUID
from datetime import datetime
from ninja import Schema, ModelSchema
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sensors.models import Sensor, SensorType, SensorCredentials


class SensorTypeSchema(ModelSchema):
    class Meta:
        model = SensorType
        exclude = ["id"]


class SensorCredentialSchema(ModelSchema):
    class Meta:
        model = SensorCredentials
        fields = ["mqtt_username", "topics", "created_at", "last_used", "is_active"]



class SensorInputSchema(Schema):
    name: str
    description: str
    sensor_type: SensorTypeSchema
    location: str
    latitude: Decimal
    longitude: Decimal
    data_format: str
    communication_mode: str
    storage_limit_gb: int = 1
    data_retention_days: int = 30
    installation_date: datetime | None = None

    model_config = {
        "json_encoders": {Decimal: lambda v: str(v)}
    }


class SensorResponseSchema(ModelSchema):
    id: UUID
    sensor_type: SensorTypeSchema
    credentials: Optional[SensorCredentialSchema] = None
    operator_id: Optional[UUID] 

    class Meta:
        model = Sensor
        fields = "__all__"


class SensorUpdateSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_format: Optional[str] = None
    communication_mode: Optional[str] = None
    storage_limit_gb: Optional[int] = None
    data_retention_days: Optional[int] = None
    installation_date: datetime | None = None

    model_config = {
        "json_encoders": {Decimal: lambda v: str(v)}
    }

class AuthenticateSensorSchema(Schema):
    mqtt_key: str
    mqtt_username: str

class AuthenticateSensorResponseSchema(Schema):
    is_authenticated: bool