# Change Log for InFlow Progress 


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

