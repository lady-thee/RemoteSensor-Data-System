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
import httpx
from loguru import logger
from asgiref.sync import async_to_sync
import secrets
from typing import  List
from asgiref.sync import async_to_sync

import bcrypt
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction, DatabaseError, IntegrityError
from django.conf import settings

from config.responses import (
    ConflictError, 
    SuccessResponseSchema, 
    NotFoundError, 
    InternalServerError
)

from sensors.models import Sensor, SensorType, SensorCredentials
from sensors.schema import (SensorInputSchema, SensorResponseSchema, SensorUpdateSchema)


User = get_user_model()


mqtt_url = settings.MQTT_SERVICE_URL
if not mqtt_url:
    mqtt_url = "localhost"
    logger.warning("MQTT_SERVICE_URL not set, defaulting to localhost")
else:
    logger.info(f"MQTT_SERVICE_URL set to {mqtt_url}")


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


async def async_request(mqtt_service_url: str, mqtt_payload: dict):
    """
    Since DJANGO signals are synchronous, this function is used to make an asynchronous HTTP request to the MQTT service.
    """
    try:
        with httpx.Client() as client:
            response = client.post(mqtt_service_url, json=mqtt_payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Successfully synced sensor status to MQTT service.")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error syncing sensor status to MQTT service: {e}")
    except httpx.RequestError as e:
        logger.error(f"Request error syncing sensor status to MQTT service: {e}")
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error syncing sensor status to MQTT service: {e}")
    except Exception as e:
        logger.error(f"Unexpected error syncing sensor status to MQTT service: {e}")



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

        # Call MQTT service to create credentials
        try:
            mqtt_service_url = f"{mqtt_url}/mqtt/create_credentials"
            mqtt_payload = {
                "mqtt_username": mqtt_username,
                "mqtt_key": raw_key,
                "topics": topics
            }
            async_to_sync(async_request)(mqtt_service_url=mqtt_service_url, mqtt_payload=mqtt_payload)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while creating MQTT credentials: {e}")
            raise ConflictError("Failed to create MQTT credentials.")

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


def verify_sensor_status_service(sensor_id: str | None = None) -> bool: 
    """
    Verify if sensor is active using sensor ID or MQTT username
    """
    try:
        if sensor_id:
            sensor = Sensor.objects.get(id=sensor_id)
        # elif mqtt_username:
        #     credentials = SensorCredentials.objects.get(mqtt_username=mqtt_username)
        #     sensor = credentials.sensor
        else:
            logger.warning("No sensor_id or mqtt_username provided for status verification")
            return False

        is_active = sensor.status == Sensor.SensorStatus.ACTIVE
        logger.info(f"Sensor status verification for {sensor.id}: {is_active}")
        return is_active
    except (Sensor.DoesNotExist, SensorCredentials.DoesNotExist):
        logger.warning(f"Sensor not found for id={sensor_id} during status verification")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during sensor status verification: {e}")
        return False



def authenticate_sensor_service(mqtt_username: str, mqtt_key: str) -> bool:
    """
    Authenticate sensor using MQTT username and key
    """
    try:
        credentials = SensorCredentials.objects.get(mqtt_username=mqtt_username)
        stored_hashed_key = credentials.mqtt_key.encode('utf-8')
        is_authenticated = bcrypt.checkpw(mqtt_key.encode('utf-8'), stored_hashed_key)
        logger.info(f"Sensor authentication result for {mqtt_username}: {is_authenticated}")
        return is_authenticated
    except SensorCredentials.DoesNotExist:
        logger.warning(f"Sensor credentials with username={mqtt_username} not found")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during sensor authentication for username={mqtt_username}: {e}")
        return False


def deactivate_sensor_service(id: str) -> SuccessResponseSchema:
    """
    Deactivate sensor by ID
    """
    try:
        sensor = Sensor.objects.get(id=id)
        sensor.status = Sensor.Status.INACTIVE
        sensor.save()
        return SuccessResponseSchema(message=f"Sensor with id '{id}' deactivated successfully.")
    except Sensor.DoesNotExist:
        logger.warning(f"Sensor with id={id} not found")
        raise NotFoundError(message=f"Sensor with id '{id}' not found.")
    except Exception as e:
        logger.exception(f"Unexpected error deactivating sensor id={id}: {e}")
        raise InternalServerError(message=f"Unexpected error deactivating sensor (Error: {e})")


def delete_sensor_service(id: str) -> SuccessResponseSchema:
    """
    Delete sensor by ID
    """
    try:
        sensor = Sensor.objects.get(id=id)
        # sensor.delete()
        sensor.status = Sensor.Status.DELETED
        sensor.save()
        return SuccessResponseSchema(message=f"Sensor with id '{id}' deleted successfully.")
    except Sensor.DoesNotExist:
        logger.warning(f"Sensor with id={id} not found")
        raise NotFoundError(message=f"Sensor with id '{id}' not found.")
    except Exception as e:
        logger.exception(f"Unexpected error deleting sensor id={id}: {e}")
        raise InternalServerError(message=f"Unexpected error deleting sensor (Error: {e})")