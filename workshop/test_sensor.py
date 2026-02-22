import os
import asyncio
import aiomqtt
from datetime import datetime
import json
import pathlib
import aiofiles

root_dir = pathlib.Path(__file__).resolve().parent

async def simulate_sensor(mqtt_username: str, mqtt_key: str, operator_id: str, sensor_id: str, payload: dict):
    """
    Simulate a sensor publishing telemetry data to the MQTT broker
    """
    BROKER = "localhost"
    topic = f"accounts/{operator_id}/sensors/{sensor_id}/telemetry"

    try:
        broker = os.getenv("MQTT_BROKER", "localhost")
        async with aiomqtt.Client(
            hostname=broker,
            port=1883,
            identifier=f"sensor_simulator_{sensor_id}",
            username=mqtt_username,
            password=mqtt_key
        ) as client:
            print(f"Sensor connected to MQTT broker at {broker}:1883")

            message_count = 0
            # Publish telemetry data every 5 seconds
            while True:
                message_count += 1

                # Update payload with timestamp and message count
                current_payload = {
                    **payload,
                    "timestamp": datetime.now().isoformat() + "Z",
                    "message_count": message_count,
                    "sensor_id": sensor_id
                }
                await client.publish(topic, json.dumps(current_payload), qos=1)
                
                async with aiofiles.open(root_dir / "test_logs" / f"mqtt_messages_{sensor_id}.log", mode="a") as f:
                    await f.write(f"{datetime.now().isoformat()} | Published to {topic}: {json.dumps(current_payload)}\n")
                # print(f"{message_count}: Published to {topic}: {current_payload}")
                await asyncio.sleep(5)
    except aiomqtt.MqttError as e:
        print(f"MQTT error in sensor simulation: {e}")
    except Exception as e:
        print(f"Error in sensor simulation: {e}")   
    

async def load_payload_from_file(file_path: str) -> dict:
    """
    Load JSON payload from a file asynchronously
    """
    try:
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        print(f"Payload file not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in payload file: {file_path}")
        return {}
    except Exception as e:
        print(f"Error loading payload from file: {e}")
        return {}


if __name__ == "__main__":
    print("🧪 MQTT Sensor Simulator\n")
    
    mqtt_username = os.getenv("MQTT_USERNAME", "sensor_dev")
    mqtt_key = os.getenv("MQTT_KEY", "dev-key")
    operator_id = os.getenv("OPERATOR_ID", "operator_dev")
    sensor_id = os.getenv("SENSOR_ID", "sensor_dev")

    payload_path = pathlib.Path(__file__).parent / "payload.json"
    print(payload_path)

    try:
        payload = asyncio.run(load_payload_from_file(str(payload_path)))
    except json.JSONDecodeError:
        print("❌ Invalid JSON. Using default payload.")
        payload = {"temperature": 25.5, "humidity": 60}
    except Exception as e:
        print(f"Error loading payload: {e}. Using default payload.")
        payload = {"temperature": 25.5, "humidity": 60}
    
    print("\n🚀 Starting sensor simulation... (Press Ctrl+C to stop)\n")
    
    try:
        asyncio.run(simulate_sensor(mqtt_username, mqtt_key, operator_id, sensor_id, payload))
    except KeyboardInterrupt:
        print("\n\n🛑 Sensor simulation stopped")