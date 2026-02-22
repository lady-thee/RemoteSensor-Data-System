"""
Defines utlities that authenticate sensors as messages are pushed to broker
"""
import os 
import time
from urllib import response
import httpx
import loguru 
import asyncio
from dotenv import load_dotenv
from async_lru_cache import alru_cache
from src.schema import SensorStatus

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

    response = None

    for attempt in range(3):  # Retry mechanism
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(auth_endpoint, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                is_authenticated = data.get("data", {}).get("is_authenticated", False)
                
                logger.info(f"Sensor authentication result for {mqtt_username}: {is_authenticated}")
                return is_authenticated
        except (httpx.HTTPError, httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"Attempt {attempt + 1}: Error during sensor authentication: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}: Unexpected error during sensor authentication: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff


@alru_cache(maxsize=128)
async def verify_sensor_status(sensor_id: str | None = None) -> SensorStatus:
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
        print("Cache hit for sensor_id:", sensor_id)
        cached_status, cached_time = sensor_status_cache[sensor_id]
        if time.time() - cached_time < 300:  # 5 minute TTL
            return cached_status
        
    # if mqtt_username and mqtt_username in sensor_status_cache:
    #     print("Cache hit for mqtt_username:", mqtt_username)
    #     cached_status, cached_time = sensor_status_cache[mqtt_username]
    #     if time.time() - cached_time < 300:  # 5 minute TTL
    #         return cached_status

    print("Cache miss for sensor_id:", sensor_id)
    user_service_url = os.getenv("MAIN_APP_API_URL", "http://localhost:8000")
    verify_endpoint = f"{user_service_url}/api/v2/sensors/verify_status"

    # params = {
    #     k: v
    #     for k, v in {
    #         "sensor_id": sensor_id,
    #         "mqtt_username": mqtt_username,
    #     }.items()
    #     if v is not None
    # }

    params = {"sensor_id": sensor_id}

    response = None

    for attempt in range(5):  # Retry mechanism
        try:
            logger.info(f"Verifying sensor status for {sensor_id} with user service. Attempt {attempt + 1}")
            async with httpx.AsyncClient() as client:
                logger.warning(f"SENDING PARAMS TO MAIN APP: {params}")
                response = await client.get(verify_endpoint, params=params, timeout=10.0)
                response.raise_for_status()
                break
                # data = response.json()
                # is_active = data.get("data", {}).get("is_active", False)

                # # Update cache
                # if is_active is not None:
                #     if sensor_id:
                #         sensor_status_cache[sensor_id] = (is_active, time.time())
                #     if mqtt_username:
                #         sensor_status_cache[mqtt_username] = (is_active, time.time())
                
                # logger.info(f"Sensor status verification result for {sensor_id or mqtt_username}: {is_active}")
                # return is_active
        except (httpx.HTTPError, httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"Attempt {attempt + 1}: Error during sensor status verification: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}: Unexpected error during sensor status verification: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    if response is None:
        logger.error(f"Failed to verify sensor status for {sensor_id} after multiple attempts.")
        return SensorStatus.UNKNOWN
    
    # Parse response
    logger.info(f"Received response from main sensor service for sensor status verification: {response.status_code} - {response.text[:200]}")
    try:
        data = response.json()
    except ValueError:
        logger.error(
            f"Invalid JSON response from main app: "
            f"status={response.status_code}, body={response.text[:200]}"
        )
        return SensorStatus.UNKNOWN
    
    status = (SensorStatus.ACTIVE if data else SensorStatus.INACTIVE)

    if status == SensorStatus.UNKNOWN:
        logger.warning(f"Sensor status is UNKNOWN for {sensor_id}. Response data: {data}")
        return status

    # Update cache with final result
    logger.info(f"Caching sensor status for {sensor_id}: {status}")
    cached_key = sensor_id
    sensor_status_cache[cached_key] = (status, time.time())
    return status