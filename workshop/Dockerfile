FROM python:3.12-slim-bookworm

WORKDIR /app

COPY . . 

RUN pip install aiomqtt 

CMD ["python", "test_sensor.py"]

