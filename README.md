# Information
This library will create an end point to train a model via flask API.
Python `3.8.5` is being used for this project.

By executing `run.sh` it will start the Flash app.

The  `TEMP_FOLDER` variable in `config.py` denotes in which folder the information will be saved.
* `TEMP_FOLDER/<process-id>/data/` contains the training data
* `TEMP_FOLDER/<process-id>/model.pkl` is the model saved after training completed.  
* `TEMP_FOLDER/<process-id>/model_temp` is the directory for auto-sklearn's temp folder.  

# Endpoints

* `/trainer/v1/trainModel` : create an auto-sklearn model.
Here unit of time is in `seconds` and unit of memory is in `MegaBytes`.
 Below is the sample request object.
  ```buildoutcfg
  {
      "data": {
        "trainingData": "https://datahub.io/machine-learning/eeg-eye-state/r/eeg-eye-state.csv",
        "dataType": "CSV",
        "targetField": "Class",
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


# Dataset

Dataset name | url | target field | Does hang?
--- | --- | --- | ---
First Order Theorem Proving | [link](https://datahub.io/machine-learning/first-order-theorem-proving/r/first-order-theorem-proving.csv) | Class | No
Phoneme | [link](https://datahub.io/machine-learning/phoneme/r/phoneme.csv) | Class | No
EEG Eye State | [link](https://datahub.io/machine-learning/eeg-eye-state/r/eeg-eye-state.csv) | Class | Yes
Blood Transfusion | [link](https://datahub.io/machine-learning/blood-transfusion-service-center/r/blood-transfusion-service-center.csv) | Class | Yes


