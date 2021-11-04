# Information
This library will create an end point to train a model via flask API.

By executing `run.sh` it will start the Flash app.

The  `TEMP_FOLDER` variable in `config.py` denotes in which folder the information will be saved.
* `TEMP_FOLDER/<process-id>/data/` contains the training data
* `TEMP_FOLDER/<process-id>/model.pkl` is the model saved after training completed.  
* `TEMP_FOLDER/<process-id>/model_temp` is the directory for auto-sklearn's temp folder.  

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