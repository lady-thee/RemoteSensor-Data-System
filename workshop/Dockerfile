FROM python:3.12-slim-bookworm

WORKDIR /app

COPY . . 

RUN pip install aiomqtt
RUN pip install aiofiles

CMD ["python", "test_sensor.py"]

