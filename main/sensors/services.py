"""
Here the service to register sensor will be in three parts:
1. Input validation for authenticated user and payload.
2. MQTT Client ID and token/key creation. The key is also encrypted or hashed
3. Returning MQTT ID key and sensor object to user. 

A service to regenerate MQTT key if previous key is forgotten or erased.
"""
import uuid
import json
import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, List

import bcrypt
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction, DatabaseError, IntegrityError
from django.utils import timezone

from config.responses import (
    ConflictError, 
    SuccessResponseSchema, 
    NotFoundError, 
    InternalServerError
)

from auth.utils import JWTUtils
from sensors.models import Sensor, SensorType, SensorCredentials
from sensors.schema import (SensorInputSchema, SensorResponseSchema, SensorUpdateSchema)


logger = logging.getLogger(__name__)
User = get_user_model()



###################################
# UTILS 
####################################
def create_sensor_type(data) -> SensorType:
    """
    Check for identical or already existing sensor type, to prevent
    redundancy during dyanmic creation. Fields are hashed for structure comparison.
    """
    data = data.model_dump()
    normalized_name = data["name"].strip().lower()
    fields_hash = hashlib.md5(json.dumps(data["fields"], sort_keys=True).encode()).hexdigest()

    existing = SensorType.objects.filter(fields_hash=fields_hash).first()
    if existing:
        return existing

    return SensorType.objects.create(name=normalized_name, fields=data["fields"], fields_hash=fields_hash)



def generate_mqtt_username(sensor_name: str, sensor_id: uuid.UUID) -> str:
    """
    Generate a readable, unique MQTT username for a sensor.
    Example: TEMP_SENSOR_A12F3B4C
    """
    name_part = sensor_name.strip().upper().replace(" ", "_")[:15]  
    id_part = str(sensor_id).split("-")[0].upper() 
    return f"{name_part}_{id_part}"



############################
# SERVICES
############################
@transaction.atomic
def register_sensor_service(user_id: str, payload: SensorInputSchema) -> SensorResponseSchema:
    try:
        operator = User.objects.get(id=user_id)

        # Validate sensor type payload
        sensor_type = create_sensor_type(payload.sensor_type)
        
        # Create sensor
        sensor = Sensor.objects.create(
            operator=operator,
            name=payload.name,
            description=payload.description,
            sensor_type=sensor_type,
            location=payload.location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            data_format=payload.data_format,
            communication_mode=payload.communication_mode,
            storage_limit_gb=payload.storage_limit_gb,
            data_retention_days=payload.data_retention_days,
            installation_date=payload.installation_date
        )

        # Generate key
        raw_key = secrets.token_urlsafe(32)

        # Hash the key 
        salt = bcrypt.gensalt()
        hashed_key = bcrypt.hashpw(raw_key.encode('utf-8'), salt).decode('utf-8')

        # Define MQTT topics 
        topics = {
            "telemetry": f"accounts/{operator.id}/sensors/{sensor.id}/telemetry",
            "control": f"accounts/{operator.id}/sensors/{sensor.id}/control",
            "status": f"accounts/{operator.id}/sensors/{sensor.id}/status",
            "alerts": f"accounts/{operator.id}/sensors/{sensor.id}/alerts"
        }

        # Generate MQTT Username
        mqtt_username = generate_mqtt_username(sensor.name, sensor.id)

        # Save hashed key and topics 
        credentials = SensorCredentials.objects.create(
            sensor=sensor,
            mqtt_key=hashed_key,
            mqtt_username=mqtt_username,
            topics=topics
        )
        print(f"MQTT KEY for sensor {sensor.name}: {raw_key} and username is: {mqtt_username}")

        logger.info(f"Successfully registered Sensor for {sensor.name}")

        return SensorResponseSchema.model_validate(
            {
                **sensor.__dict__,
                "sensor_type": sensor_type,
                "credentials": credentials
            }
        )
    except ValidationError as e:
        logger.exception(f"Error during tokenization: {e}")
        raise ConflictError(f"There was a problem during sensor registration, please try again later")
    except User.DoesNotExist:
        logger.warning(f"User with id={user_id} not found")
        raise NotFoundError(message=f"User with id '{user_id}' not found.")
    except IntegrityError as e:
        logger.exception(f"Database integrity error while creating sensor: {e}")
        raise ConflictError(message="Database integrity error while creating sensor.")
    except DatabaseError as e:
        logger.exception(f"Database error while creating sensor: {e}")
        raise InternalServerError(message="Database operation failed.")



def get_user_sensors_service(user_id: str) -> List[SensorResponseSchema]:
    """
    Get sensors for authenticated user 
    """
    try:
        sensors = Sensor.objects.filter(operator=user_id).order_by("created_at")
        return [SensorResponseSchema.model_validate(sensor) for sensor in sensors]
    except User.DoesNotExist:
        logger.warning(f"User with id={user_id} not found")
        raise NotFoundError(message=f"User with id '{user_id}' not found.")
    except Exception as e:
        logger.exception(f"Unexpected error fetching sensors with user id={user_id}: {e}")
        raise InternalServerError(message=f"Unexpected error fetching sensors (Error: {e})")



def get_sensor_by_id_service(id: str) -> SensorResponseSchema:
    """
    Get sensor by ID
    """
    try: 
        sensor = Sensor.objects.get(id=id)
        return SensorResponseSchema.model_validate(sensor) 
    except Sensor.DoesNotExist:
        logger.warning(f"Sensor with id={id} not found")
        raise NotFoundError(message=f"Sensor with id '{id}' not found.")
    except Exception as e:
        logger.exception(f"Unexpected error fetching user id={id}: {e}")
        raise InternalServerError(message=f"Unexpected error fetching user (Error: {e})")


def update_sensor_service(id: str, data: SensorUpdateSchema) -> SensorResponseSchema:
    """
    Update sensor 
    """
    try: 
        payload = data.model_dump(exclude_none=True)
        sensor = Sensor.objects.get(id=id)
        
        for field, value in payload.items():
            setattr(sensor, field, value)

        sensor.save()
        return SensorResponseSchema.model_validate(sensor)
    except Sensor.DoesNotExist:
        logger.warning(f"Sensor with id={id} not found")
        raise NotFoundError(message=f"Sensor with id '{id}' not found.")
    except Exception as e:
        logger.exception(f"Unexpected error fetching user id={id}: {e}")
        raise InternalServerError(message=f"Unexpected error fetching user (Error: {e})")