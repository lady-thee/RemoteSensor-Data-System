# Change Log for InFlow Progress 


## [2026-2-22]
### Features
- Added MQTT sensor status verification via main app service API.
- Implemented optional query parameters `sensor_id` and `mqtt_username` for sensor verification endpoint.
- Added file logging of MQTT messages per sensor for debugging purposes.

### Updates
- Updated `verify_sensor_status` endpoint to correctly handle optional parameters and raise a 400 error if neither parameter is provided.
- Updated Docker setup to ensure MQTT service writes logs to `/app/src/data`.
- Updated Docker Compose configuration to mount `./data` folder as a volume for MQTT service, allowing logs to be visible on the host system.
- Improved retry and logging logic in MQTT service for sensor status verification.
- Cleaned up cache logic for sensor verification in MQTT service to prevent repeated API calls for recently verified sensors.

### Fixes
- Fixed issue where MQTT service requests were failing with `422 Unprocessable Entity` due to improper handling of optional parameters.
- Fixed file creation issue inside Docker by ensuring parent directories exist before writing logs.
- Resolved `DisallowedHost` errors in main app service by correctly adding container hostnames to `ALLOWED_HOSTS`.

## [2026-2-9]
### Features
- Created a script to simulate sensor behavior to test MQTT conenction with mosquito
- Created dockerfile for script to enable it run in docker environment.


## [2026-1-23]
### Updates
- Updated sensor status in the models.py, to include DELETE type.
- Updated the MQTT listener to verify sensor status upon every message before processing. 
- Updated the verify sensor route in MQTT routes. 
- Added an index atrribute to the Sensor.Status field. 

### Features
- Created signals for the Create sensor endpoint.
- Created two new services for deleting sensors and deactivating sensor
- Created a new service to verify sensor status in the sensor services.py and views.py
- Added a new fucntion to the auth.py of the MQTT service to call the verify sensor status sensor on the main app url. 
- Implemented a simple in-memory cache, to test cache set up. Would migrate to redis in due time.


## [2026-1-18]

### Features
- Created functions for authenticating sensors on the mqtt service and the main/sensor service.
- Created dockerfile for mqtt service.
- Created routes/APIs for further authentication and verification in the mqtt service.
- Created schemas for requests and response of credentials.
- Implemented a write to file script for testing purposes. 
- Created a parser fucntion and mqtt listener for managing the broker connection in the mtt service. 

