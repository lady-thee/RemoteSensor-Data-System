FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

# Set the working directory to inside container
WORKDIR /app

# RUN echo "Acquire::Check-Valid-Until \"false\";\nAcquire::Check-Date \"false\";" | cat > /etc/apt/apt.conf.d/10no--check-valid-until

# Install OS level dependencies
RUN apt-get update \
    && apt-get -y install --no-install-recommends -y \
        build-essential \
        libpq-dev gcc \
        gcc \
        postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

# Install Pipenv globally
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --categories packages

COPY . . 

RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run Daphne for ASGI connections
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]