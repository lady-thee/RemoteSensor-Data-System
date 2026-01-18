from typing import Dict, Any 
from pydantic import BaseModel


class SensorData(BaseModel):
    mqtt_key: str 
    data: Dict[str, Any]

