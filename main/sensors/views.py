from typing import List
from django.contrib.auth import get_user_model
from ninja import Router

from sensors.services import (
    register_sensor_service,
    get_sensor_by_id_service,
    get_user_sensors_service,
    update_sensor_service,
    authenticate_sensor_service,
    deactivate_sensor_service,
    delete_sensor_service,
    verify_sensor_status_service
)
from sensors.schema import (
    SensorInputSchema, 
    SensorResponseSchema, 
    SensorUpdateSchema, 
    AuthenticateSensorSchema,
    AuthenticateSensorResponseSchema
)
from config.responses import (SuccessResponseSchema, ErrorCode)
from config.dependencies import authenticate_user

User = get_user_model()

router = Router(tags=["sensors"])


@router.post(
    "/register",
    response={201: SuccessResponseSchema[SensorResponseSchema]},
    auth=authenticate_user,
    summary="Register sensor"
)
def register_sensor(request, payload: SensorInputSchema):
    """
    Register new sensor 
    """
    current_user = request.auth
    sensor_data = register_sensor_service(str(current_user.id), payload)

    return SuccessResponseSchema[SensorResponseSchema](
        status=ErrorCode.SUCCESS.value,
        message="Sensor registered successsfully",
        data=sensor_data
    )



@router.get(
    "/users",
    response={200: SuccessResponseSchema[List[SensorResponseSchema]]},
    auth=authenticate_user,
    summary="Get sensors for current user"
)
def get_sensor_for_current_users(request):
    """
    Get sensors fur current user
    """
    current_user = request.auth
    sensor_data = get_user_sensors_service(str(current_user.id))

    return SuccessResponseSchema[List[SensorResponseSchema]](
        status=ErrorCode.SUCCESS.value,
        message="Records retrieved successsfully",
        data=sensor_data
    )


@router.get(
    "/user/{sensor_id}",
    response={200: SuccessResponseSchema[SensorResponseSchema]},
    auth=authenticate_user,
    summary="Get sensors for current user"
)
def get_sensor_per_id(request, sensor_id: str):
    """
    Get sensor by id
    """
    # current_user = request.auth 
    sensor_data = get_sensor_by_id_service(str(sensor_id))
    
    return SuccessResponseSchema[SensorResponseSchema](
        status=ErrorCode.SUCCESS.value,
        message="Records retrieved successsfully",
        data=sensor_data
    )


@router.patch(
    "/update/{sensor_id}",
    response={200: SuccessResponseSchema[SensorResponseSchema]},
    auth=authenticate_user,
    summary="Update sensor"
)
def update_sensor(request, sensor_id: str, payload: SensorUpdateSchema):
    """
    Update sensor 
    """

    # current_user = request.auth

    sensor_data = update_sensor_service(str(sensor_id), payload)
    
    return SuccessResponseSchema[SensorResponseSchema](
        status=ErrorCode.SUCCESS.value,
        message="Sensor updated successsfully",
        data=sensor_data
    )


@router.get(
    "/verify_status",
    response={200: bool},
    summary="Verify if sensor is active"
)
def verify_sensor_status(request, sensor_id: str = None, mqtt_username: str = None):
    """
    Verify if sensor is active
    """
    is_active = verify_sensor_status_service(sensor_id=sensor_id, mqtt_username=mqtt_username)
    
    return is_active


@router.post(
    "/authenticate",
    response={200: SuccessResponseSchema[AuthenticateSensorResponseSchema]},
    summary="Authenticate sensor"
)
def authenticate_sensor(request, payload: AuthenticateSensorSchema):
    """
    Authenticate sensor using MQTT username and key
    """
    is_authenticated = authenticate_sensor_service(
        mqtt_username=payload.mqtt_username,
        mqtt_key=payload.mqtt_key
    )

    return SuccessResponseSchema[AuthenticateSensorResponseSchema](
        status=ErrorCode.SUCCESS.value,
        message="Sensor authentication processed successfully",
        data=AuthenticateSensorResponseSchema(is_authenticated=is_authenticated)
    )


@router.patch(
    "/deactivate/{sensor_id}",
    response={200: SuccessResponseSchema[None]},
    auth=authenticate_user,
    summary="Deactivate sensor"
)
def deactivate_sensor(request, sensor_id: str):
    """
    Deactivate sensor - To be implemented in future releases
    """
    # current_user = request.auth

    deactivate_response = deactivate_sensor_service(str(sensor_id))
    
    return deactivate_response


@router.patch(
    "/delete/{sensor_id}",
    response={200: SuccessResponseSchema[None]},
    auth=authenticate_user,
    summary="Delete sensor"
)
def delete_sensor(request, sensor_id: str):
    """
    Delete sensor - soft delete by changing status to DELETED
    """
    # current_user = request.auth

    delete_response = delete_sensor_service(str(sensor_id))
    
    return delete_response