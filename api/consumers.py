import asyncio

# import json
# import requests
import logging

# from datetime import timedelta
# from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from api.models import SensorData
from api.serializers import SensorDataDetailsSerializer

# from django.core.serializers.json import DjangoJSONEncoder
# from django.db.models import F
# from django.utils import timezone


logger = logging.getLogger(__name__)  # logging


class SensorConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.last_sent_data = None

    async def disconnect(self, close_code):
        logger.info("WebSocket disconnected with code: %s", close_code)

    async def receive_json(self, content, **kwargs):
        try:
            action = content.get("action")

            if action == "request.data":
                await self.send_sensor_data()

        except Exception as e:
            print(f"Exception in receive_json: {e}")

    def connection_open(self):
        return True

    @database_sync_to_async
    def sensor_data(self):
        queryset = SensorData.objects.all()
        serializer = SensorDataDetailsSerializer(queryset, many=True)
        if serializer.data:
            #   print(serializer.data[1])
            return serializer.data
        else:
            print("Serializer is not valid", queryset)

    async def send_sensor_data(self, **kwargs):
        while self.connection_open():
            sensor_data = await self.sensor_data()
            if sensor_data != self.last_sent_data:
                # print("Sending sensor data:", sensor_data)
                await self.send_json(sensor_data)
                self.last_sent_data = sensor_data
            await asyncio.sleep(3)
