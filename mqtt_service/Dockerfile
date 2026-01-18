FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

# Set the working directory to inside container
WORKDIR /app

# Install OS level dependencies
RUN apt-get update && \
    apt-get install -y mosquitto-clients && \
    rm -rf /var/lib/apt/lists/*

# Install Pipenv globally
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --categories packages

COPY . . 

# Expose port
EXPOSE 8001

# Run the MQTT service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]