import os 
import asyncio
from datetime import datetime
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from src.handler import mqtt_listener
from src.routes import router as mqtt_router

load_dotenv()

background_task = None
influx_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events
    """
    # Startup code
    logger.info("Starting MQTT Service...")
    background_task = asyncio.create_task(mqtt_listener())
    logger.info("MQTT Listener task started.")

    yield 

    # Shutdown code
    logger.info("Shutting down MQTT Service...")
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            logger.info("MQTT Listener task cancelled.")
    
    # if influx_client:
    #     influx_client.close()
    #     logger.info("InfluxDB client closed.")
    logger.info("MQTT Service shut down complete.")




app = FastAPI(
    title="MQTT Authentication Service",
    description="Service to handle MQTT authentication for sensors",
    lifespan=lifespan,
    version="1.0.0"
)


app.include_router(mqtt_router)



@app.get("/")
async def root():
    return {
        "service": "MQTT Service",
        "status": "running",
        "message": "MQTT Service is running"
    }

@app.get("/health")
async def health_check():
    return {
        "mqtt_listener": "running" if background_task and not background_task.done() else "stopped",
        # "influxdb": "connected" if influx_client else "disconnected",
        "broker": os.getenv("MQTT_BROKER"),
        "timestamp": datetime.now().isoformat()
    }
