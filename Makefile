.PHONY: help up down build logs restart shell migrate makemigrations psql

help: 
	@echo "Available commands:"
	@echo "  make up              Start services in detached mode"
	@echo "  make down            Stop and remove containers/networks"
	@echo "  make build           Build or rebuild services"
	@echo "  make logs            Follow logs for all services"
	@echo "  make restart         Restart all services"
	@echo "  make migrate         Run Django migrations"
	@echo "  make migrations  Create new Django migrations"
	@echo "  make shell           Enter the Django shell"
	@echo "  make bash            Enter the Main App container bash"
	@echo "  make psql            Enter the Postgres database"

up: 
	docker compose up

down:
	docker compose down 

down-all:
	docker compose down --volumes --remove-orphans

build:
	docker compose up -d --build 

logs:
	docker compose logs -f 

restart:
	docker compose restart 


# Django related commands 
migrations: 
	docker compose exec main_app_service python manage.py makemigrations 

migrate:
	docker compose exec main_app_service python manage.py migrate 

superuser:
	docker compose exec main_app_service python manage.py createsuperuser 

shell:
	docker compose exec main_app_service python manage.py shell 

bash:
	docker compose exec main_app_service python manage.py /bin/bash 


# PostgreSQL commands
psql:
	docker compose exec postgresql_db psql -U ${PG_USER} -d ${PG_DB}

