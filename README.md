# Information
This library will create an end point to train a model via flask API.

By executing `run.sh` it will start the Flash app.

# Endpoints

* `/trainer/v1/trainModel` : create an auto-sklearn model. Below is the sample request object.
  ```buildoutcfg
  {
      "data": {
        "trainingData": "https://archive.ics.uci.edu/ml/machine-learning-databases/00264/EEG%20Eye%20State.arff",
        "dataType": "ARFF",
        "targetField": "eyeDetection",
        "modelType": "CLASSIFICATION"
      },
      "modelConfig": {
        "totalTime": 200,
        "timePerRun": 20,
        "memoryLimit": 2024,
        "ensembleSize": 50
      }
   }
    ```
  It will return a process id, which will help to find the status of that process.
* `/trainer/v1/getStatus` : It will return status of a training process. Below is the request object
    ```buildoutcfg
    {
      "processId": "<process id get from trainModel end point>"
    }
    ```
    
# Docker Service Up
```buildoutcfg
docker-compose up
```
### Rebuilt Image and Run
```
docker-compose up --build
```
# Access Swagger
```
http://localhost:9094/
```
# Docker Service Down
```
docker-compose down
```

**Note:**
 - Saved models are mounted in current directory under `models/`
