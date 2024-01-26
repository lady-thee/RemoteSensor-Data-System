## Introduction

The SensorFusion API represents a sophisticated backend system designed to support weather and temperature remote sensors. Its primary function is to collect and manage data pertaining to weather conditions in specific areas, offering both real-time analysis and archiving capabilities. Built upon the robust Django/Django Rest Framework for APIs, this system is deployed using Docker containerization, ensuring seamless operation and scalability.

## Key Features

- **Weather Data Collection:** The system efficiently gathers and stores reliable data from remote sensors, providing insights into weather conditions in real time.
- **Temperature Monitoring:** With a focus on temperature sensors, the API enables the collection and analysis of temperature-related data, aiding in understanding temperature variations.

## Technical Infrastructures

The SensorFusion API harnesses the power of a relational database management system, specifically PostgreSQL, to manage and organize the collected sensor data effectively. This choice of PostgreSQL ensures a robust and scalable database solution, providing reliability and flexibility in handling complex data relationships.

## Advantages

- **Data Reliability:** Leveraging PostgreSQL's capabilities, the system guarantees the integrity and reliability of stored sensor data, ensuring accuracy for subsequent analysis and retrieval.
- **Scalability and Flexibility:** By utilizing Docker for deployment and PostgreSQL for data management, the system is poised for scalability, accommodating potential future expansions and increased data volumes without compromising efficiency.

The SensorFusion API stands as a comprehensive solution, proficiently managing weather and temperature sensor data through a well-structured backend architecture, bolstered by PostgreSQL's capabilities as its chosen relational database management system.

# Prerequisites
1. Python(3.8 or higher)
2. Django
3. Django Rest Framework
4. Docker, Docker-Compose
5. Django channels
6. A virtual environment

## Architecture

See [link-to-diagram](https://www.notion.so/System-Architecture-Documentation-d5a409418bce420597adfcfcd49cda95?pvs=21) to view the system architecture schema

## Database Schema

See [link-to-diagram](https://drawsql.app/teams/the-a-team-9/diagrams/remote-sensor-data-aggregator) to view Database schema 

## API Documentation

See [link-to-doc](http://localhost:8000/api/docs/redoc/) to view API documentation on Swagger UI and see [this](https://www.notion.so/API-Documentation-37eadfdd597f4362a9ed4b21a4cf2dc0?pvs=21) to view comprehensive documentation on APIs.


### Got an issue?
Raise an issue!