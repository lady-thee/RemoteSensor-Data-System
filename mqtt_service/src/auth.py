"""
Defines utlities that authenticate sensors as messages are pushed to broker
"""
import os 
import time
import httpx
import loguru 
from dotenv import load_dotenv
from async_lru_cache import alru_cache

load_dotenv()

logger = loguru.logger

# In memory cache with TTL for dev purposes
sensor_status_cache = {}

async def authenticate_sensor(mqtt_key: str, mqtt_username: str) -> bool:
    """
    Authenticates a sensor using an external user service.

    Args:
        mqtt_key: The MQTT key provided by the sensor.
        mqtt_username: The MQTT username provided by the sensor.

    Returns:
        bool: True if authentication is successful, False otherwise.
    """
    user_service_url = os.getenv("MAIN_SERVICE_API_URL", "http://localhost:8000")
    auth_endpoint = f"{user_service_url}/api/v2/sensors/authenticate"

    payload = {
        "mqtt_key": mqtt_key,
        "mqtt_username": mqtt_username
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(auth_endpoint, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            is_authenticated = data.get("data", {}).get("is_authenticated", False)
            
            logger.info(f"Sensor authentication result for {mqtt_username}: {is_authenticated}")
            return is_authenticated
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during sensor authentication: {e}")
        return False
    except httpx.RequestError as e:
        logger.error(f"Request error during sensor authentication: {e}")
        return False
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error during sensor authentication: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during sensor authentication: {e}")
        return False


@alru_cache(maxsize=128)
async def verify_sensor_status(sensor_id: str | None = None, mqtt_username: str | None = None) -> bool:
    """
    Verifies if a sensor is active using an external user service.

    Args:
        sensor_id: The ID of the sensor to verify.
        mqtt_username: The MQTT username of the sensor to verify.
    Returns:
        bool: True if the sensor is active, False otherwise.
    """

    # Check Cache first
    if sensor_id and sensor_id in sensor_status_cache:
        cached_status, cached_time = sensor_status_cache[sensor_id]
        if time.time() - cached_time < 300:  # 5 minute TTL
            return cached_status
        
    if mqtt_username and mqtt_username in sensor_status_cache:
        cached_status, cached_time = sensor_status_cache[mqtt_username]
        if time.time() - cached_time < 300:  # 5 minute TTL
            return cached_status

    user_service_url = os.getenv("MAIN_SERVICE_API_URL", "http://localhost:8000")
    verify_endpoint = f"{user_service_url}/api/v2/sensors/verify_status"

    params = {}
    if sensor_id:
        params["sensor_id"] = sensor_id
    if mqtt_username:
        params["mqtt_username"] = mqtt_username

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(verify_endpoint, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            is_active = data.get("data", {}).get("is_active", False)

            # Update cache
            sensor_status_cache[sensor_id] = (is_active, time.time())
            
            logger.info(f"Sensor status verification result for {sensor_id or mqtt_username}: {is_active}")
            return is_active
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during sensor status verification: {e}")
        return False
    except httpx.RequestError as e:
        logger.error(f"Request error during sensor status verification: {e}")
        return False
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error during sensor status verification: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during sensor status verification: {e}")
        return False