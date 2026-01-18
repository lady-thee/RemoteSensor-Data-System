from pydantic import BaseModel



class CreateCredentialsRequest(BaseModel):
    mqtt_username: str
    mqtt_key: str

class CreateCredentialsResponse(BaseModel):
    status: str
    message: str
    mqtt_username: str


class DeleteCredentialsRequest(BaseModel):
    mqtt_username: str

class DeleteCredentialsResponse(BaseModel):
    status: str
    message: str
