"""
Defines utlities that authenticate sensors as messages are pushed to broker
"""
import os 
import httpx
import loguru 
from dotenv import load_dotenv

load_dotenv()
logger = loguru.logger

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

