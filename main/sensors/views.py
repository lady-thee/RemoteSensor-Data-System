from typing import List
from django.contrib.auth import get_user_model
from ninja import Router, Schema, PatchDict

from sensors.services import (
    register_sensor_service,
    get_sensor_by_id_service,
    get_user_sensors_service,
    update_sensor_service
)
from sensors.models import Sensor, SensorType, SensorCredentials
from sensors.schema import (SensorInputSchema, SensorResponseSchema, SensorUpdateSchema)
from config.responses import (SuccessResponseSchema, NotFoundError, ErrorCode)
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
    "/users/{sensor_id}",
    response={200: SuccessResponseSchema[SensorResponseSchema]},
    auth=authenticate_user,
    summary="Get sensors for current user"
)
def get_sensor_per_id(request, sensor_id: str):
    """
    Get sensor by id
    """
    current_user = request.auth 
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

    current_user = request.auth

    sensor_data = update_sensor_service(str(sensor_id), payload)
    
    return SuccessResponseSchema[SensorResponseSchema](
        status=ErrorCode.SUCCESS.value,
        message="Sensor updated successsfully",
        data=sensor_data
    )
