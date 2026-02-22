"""
Defines the handler that establishes the broker with Mosquito, using asyncio_mqtt
Handles incoming messages as well
"""
import os
import json
import asyncio
from loguru import logger
import aiomqtt
import aiofiles
from datetime import datetime
from dotenv import load_dotenv
import pathlib

from src.auth import verify_sensor_status
from src.schema import SensorStatus

root_dir = pathlib.Path(__file__).resolve().parent

load_dotenv()


def parse_topic(topic: str):
    """
    Parse topic format: accounts/{operator_id}/sensors/{sensor_id}/{type}
    Returns: (operator_id, sensor_id, topic_type)
    """
    try:
        parts = topic.split('/')
        if len(parts) >= 5 and parts[0] == "accounts" and parts[2] == "sensors": 
            operator_id = parts[1]
            sensor_id = parts[3]
            topic_type = parts[4] if len(parts) > 4 else "Unknown"
            return operator_id, sensor_id, topic_type 
        return None, None, None
    except Exception as e:
        logger.error(f"Error parsing topic {topic}: {e}")
        return None, None, None


async def mqtt_listener():
    """
    Background task that continously listens for MQTT messages

    Main MQTT listner that:
    1. Connects to the Mosquitto broker
    2. Subscribes to all sensor topics
    3. Listens for incoming messages
    4. Parses topic to extract operator_id and sensor_id
    5. Saves to InfluxDB
    6. Handles errors and reconnections
    """

    broker = os.getenv("MQTT_BROKER", "localhost")
    port = int(os.getenv("MQTT_PORT", 1883))

    try:
        async with aiomqtt.Client(
            hostname=broker,
            port=port,
            identifier="inflow_mqtt_listener"
        ) as client:
            logger.info(f"Connected to MQTT broker at {broker}:{port}")

            # Subscribe to all sensor topics using wildcards
            await client.subscribe("accounts/+/sensors/+/telemetry")
            await client.subscribe("accounts/+/sensors/+/status")
            await client.subscribe("accounts/+/sensors/+/alerts")
            await client.subscribe("accounts/+/sensors/+/control")

            logger.info("Subscribed to all sensors topics  (accounts/+/sensors/+/*)")

            # Listen for messages continuously
            async for message in client.messages:
                topic = message.topic.value
                payload_str = message.payload.decode()

                print(f"Received: {topic}")

                logger.info("Topic is received")

                # Parse topic to extract IDs
                operator_id, sensor_id, topic_type = parse_topic(topic)

                if not operator_id or not sensor_id:
                    logger.error(f"MQTT_ERROR: Invalid topic format: {topic}")
                    continue
                
                # Verify messsage/payload before processing
                is_sensor_active = await verify_sensor_status(sensor_id=sensor_id)

                if is_sensor_active == SensorStatus.INACTIVE:
                    logger.error(f"MQTT_ERROR: Inactive sensor {sensor_id}. Rejecting message.")
                    continue

                # Parse payload if sensor is active
                try: 
                    payload = json.loads(payload_str)
                except json.JSONDecodeError:
                    logger.debug(f"Invalid JSON Payload: {payload_str}")
                    # Store as raw string if not JSON
                    payload = {
                        "raw_data": payload_str
                    }

                logger.info(f"Parsed message from Operator: {operator_id}, Sensor: {sensor_id}, Type: {topic_type}, Payload: {payload}")

                # write to file for testing
                async with aiofiles.open(root_dir / "data" / f"mqtt_messages_{sensor_id}.log", mode="a") as f:
                    await f.write(f"{datetime.now().isoformat()} | Published to {topic}: {json.dumps(payload)}\n")
                
                # Save to influxDB               
    except aiomqtt.MqttError as e:
        print(f"MQTT Error: {e}")
    except asyncio.CancelledError:
        print("MQTT listener cancelled")
    except Exception as e:
        print(f"Unexpected error: {e}")

