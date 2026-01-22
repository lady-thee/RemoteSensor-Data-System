import loguru
import subprocess

from fastapi import APIRouter 
from fastapi.exceptions import HTTPException
from src.schema import (
    CreateCredentialsRequest, 
    CreateCredentialsResponse,
    DeleteCredentialsRequest,
    DeleteCredentialsResponse
)

from src.auth import authenticate_sensor

logger = loguru.logger


router = APIRouter(
    prefix="/mqtt",
    tags=["mqtt_authentication"]
)

# Routes for MQTT credentials management
@router.post(
    "/create_credentials",
    response_model=CreateCredentialsResponse,
    summary="Create MQTT credentials for a sensor on Mosquitto broker"
)
async def create_credentials(request: CreateCredentialsRequest):
    """
    Create MQTT credentials for a sensor on Mosquitto broker
    """
    try:
        import subprocess
        subprocess.run(
            [
                'mosquitto_passwd',
                '-b',
                '/mosquitto/config/passwd',
                request.mqtt_username,
                request.mqtt_key
            ],
            capture_output=True,
            text=True,
            check=True
        )

        # Reload Mosquitto to apply changes
        subprocess.run(
            ['kill', '-SIGHUP', '1'],
            capture_output=True,
            check=True
        )

        logger.info(f"MQTT credentials created for {request.mqtt_username}")

        return CreateCredentialsResponse(
            status="success",
            message="Credentials created successfully",
            mqtt_username=request.mqtt_username
        )
    except subprocess.CalledProcessError as e:
        return CreateCredentialsResponse(
            status="error",
            message=f"Failed to create credentials: {e.stderr}",
            mqtt_username=request.mqtt_username
        )
    except Exception as e:
        logger.error(f"Unexpected error creating MQTT credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/verify/{mqtt_username}/{mqtt_key}",
)
async def verify_mqtt_credentials(mqtt_username: str, mqtt_key: str):
    """
    Verify MQTT credentials for a sensor on Mosquitto broker - called by MQTT listener 
    when data is received. This checks both the Mosquitto passwd file and verifies the sensor
    via the main database service.
    """
    try:
        # Check if credentials exist in Mosquitto passwd file
        result = subprocess.run(
            [
                ['grep', '-c', f'^{mqtt_username}:{mqtt_key}$', '/mosquitto/config/passwd']
            ],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.info(f"MQTT credentials verification failed for {mqtt_username}")
            return {
                "status": "error", 
                "message": "Credentials are not found in Mosquitto.",
                "is_valid": False
            }

        logger.info(f"MQTT credentials found in Mosquitto for {mqtt_username}")

        # Verify Sensor via MAIN DB for added security
        is_authenticated = await authenticate_sensor(
            mqtt_key=mqtt_key,
            mqtt_username=mqtt_username
        )
        if not is_authenticated:
            logger.info(f"MQTT credentials verification failed in main DB for {mqtt_username}")

            # Clean up - remove from Mosquitto as well
            # subprocess.run(
            #     [
            #         'mosquitto_passwd',
            #         '-D',
            #         '/mosquitto/config/passwd',
            #         mqtt_username
            #     ],
            #     capture_output=True,
            #     text=True,
            #     check=True
            # )
            await delete_credentials(DeleteCredentialsRequest(mqtt_username=mqtt_username))
            return {
                "status": "error", 
                "message": "Sensor is not active or does not exist at all in main DB.",
                "is_valid": False
            }
        
        logger.info(f"MQTT credentials verified successfully for {mqtt_username}")
        return {
            "status": "success", 
            "message": "Credentials are valid and sensor is active",
            "is_valid": True
        }
    except Exception as e:
        logger.error(f"Unexpected error verifying MQTT credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

@router.delete(
    "/delete_credentials",
    response_model=DeleteCredentialsResponse,
    summary="Delete MQTT credentials for a sensor on Mosquitto broker"
)
async def delete_credentials(request: DeleteCredentialsRequest):
    """
    Delete MQTT credentials for a sensor on Mosquitto broker
    """
    try:
        subprocess.run(
            [
                'mosquitto_passwd',
                '-D',
                '/mosquitto/config/passwd',
                request.mqtt_username
            ],
            capture_output=True,
            text=True,
            check=True
        )

        # Reload Mosquitto to apply changes
        subprocess.run(
            ['kill', '-SIGHUP', '1'],
            capture_output=True,
            check=True
        )

        logger.info(f"MQTT credentials deleted for {request.mqtt_username}")

        return DeleteCredentialsResponse(
            status="success",
            message="Credentials deleted successfully"
        )
    except subprocess.CalledProcessError as e:
        return DeleteCredentialsResponse(
            status="error",
            message=f"Failed to delete credentials: {e.stderr}"
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting MQTT credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")