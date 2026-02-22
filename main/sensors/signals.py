from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.conf import settings
from sensors.models import  Sensor, SensorCredentials
import loguru
from asgiref.sync import async_to_sync
import httpx

logger = loguru.logger

"""
This module contains signals to sync sensor credentials with the MQTT service
whenever a sensor is created, updated, or deleted. This is important to ensure 
mosquitto broker has the up to date credentials for authenticating sensors to prevent a stale
connection or data push attempts.
"""


async def delete_mqtt_credentials_request(mqtt_service_url: str, payload: dict):
    """
    Since DJANGO signals are synchronous, this function is used to make an asynchronous HTTP request to the MQTT service to delete credentials.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(mqtt_service_url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Successfully deleted MQTT credentials for sensor from MQTT service.")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error deleting MQTT credentials for sensor: {e}")
    except httpx.RequestError as e:
        logger.error(f"Request error deleting MQTT credentials for sensor: {e}")
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error deleting MQTT credentials for sensor: {e}")
    except Exception as e:
        logger.error(f"Unexpected error deleting MQTT credentials for sensor: {e}")


@receiver(post_save, sender=Sensor)
def sync_sensor_credentials_to_mqtt_service(sender, instance, created, **kwargs):
    """
    Sync sensor credentials to MQTT service when a sensor status is changed.
    """
    if created:
        return  
    mqtt_service_url = f"{settings.MQTT_SERVICE_URL}/mqtt/delete_credentials"
    sensor_id = str(instance.id)
    try:
        mqtt_username = SensorCredentials.objects.get(sensor=instance).mqtt_username
    except SensorCredentials.DoesNotExist:
        logger.warning(f"No MQTT credentials found for deleted sensor {sensor_id}. Skipping deletion on MQTT service.")
        return
    
    if instance.status == Sensor.SensorStatus.INACTIVE:
        # Deactivate credentials on Mosquitto broker
        payload = {
            "mqtt_username": mqtt_username
        }
        try:
            
            async_to_sync(delete_mqtt_credentials_request)(mqtt_service_url=mqtt_service_url, payload=payload)
            logger.info(f"Successfully synced sensor {sensor_id} INACTIVE status to MQTT service by deleting credentials.")
        except Exception as e:
            logger.error(f"Unexpected error syncing credentials to MQTT service for sensor {sensor_id}: {e}")



@receiver(post_delete, sender=Sensor)
def delete_mqtt_credentials(sender, instance, **kwargs):
    """
    Delete MQTT credentials from Mosquitto broker when sensor is deleted.
    """
    mqtt_service_url = f"{settings.MQTT_SERVICE_URL}/mqtt/delete_credentials"
    sensor_id = str(instance.id)
    try:
        mqtt_username = SensorCredentials.objects.get(sensor=instance).mqtt_username
    except SensorCredentials.DoesNotExist:
        logger.warning(f"No MQTT credentials found for deleted sensor {sensor_id}. Skipping deletion on MQTT service.")
        return

    payload = {
        "mqtt_username": mqtt_username
    }
    try:
        async_to_sync(delete_mqtt_credentials_request)(mqtt_service_url=mqtt_service_url, payload=payload)
        logger.info(f"Successfully deleted MQTT credentials for deleted sensor {sensor_id} from MQTT service.")
    except Exception as e:
        logger.error(f"Unexpected error deleting MQTT credentials for sensor {sensor_id}: {e}")