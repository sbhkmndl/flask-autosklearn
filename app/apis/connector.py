import json
import logging
from enum import Enum
from multiprocessing import Process

from flask import Flask, Blueprint, Response, request
from flask_restplus import Api, Resource, fields, reqparse

from app.apis.data import Data
from app.core.C import get_unique_id
from app.core.trainer import Trainer
from config import DRIVER_CONNECTOR_APIS, CONNECTOR, DESCRIPTION, TITLE, VERSION, API_VERSION, BASE

blueprint = Blueprint('api', __name__)
app = Flask(__name__)
api = Api(blueprint, version=VERSION, title=TITLE,
          description=DESCRIPTION,
          default=CONNECTOR, default_label=DRIVER_CONNECTOR_APIS
          )
logging.basicConfig(level=logging.DEBUG)

train_data = api.model("TrainingData", {
    'trainingData': fields.Url(description='training data URL', required=True),
    'dataType': fields.String(description='training data type', required=True, enum=['CSV', 'ARFF']),
    'targetField': fields.String(description='training data target field name', required=True),
    'modelType': fields.String(description='model type CLASSIFICATION/REGRESSION',
                               enum=['CLASSIFICATION', 'REGRESSION'], required=True),
    # 'ignoreColumns': fields.List(fields.String, description="ignore column names")
})
model_config = api.model("ModelConfig", {
    "totalTime": fields.Integer(description="total time for training in seconds", required=True),
    "timePerRun": fields.Integer(description="time per run in seconds", required=True),
    "memoryLimit": fields.Integer(description="memory limit in MB", required=True),
    "ensembleSize": fields.Integer(description="ensemble size")
})
train_model_request_obj = api.model('TrainingModelRequestObject', {
    "data": fields.Nested(train_data),
    "modelConfig": fields.Nested(model_config)
})

status_request_args = reqparse.RequestParser()
status_request_args.add_argument('processId', type=str,
                                 help="process id get from /trainModel end point", required=True)


class ResponseStatus(str, Enum):
    TRAINING_SUCCESS = 'TRAINING_SUCCESS'
    DATA_ERROR = 'DATA_ERROR'
    NEURAL_NETWORK_ERROR = 'NEURAL_NETWORK_ERROR'
    RESOURCE_LIMIT_ERROR = 'RESOURCE_LIMIT_ERROR'


@api.route(BASE + '/ping')
class PingOperation(Resource):
    @api.response(200, json.dumps({"message": "i am alive"}))
    def get(self):
        """
        Ping the driver connector
        """
        logging.info("ping")
        return Response(json.dumps({"message": "pinging successfully!"}), 200)


@api.route(BASE + API_VERSION + '/trainModel')
class RunOperation(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @api.response(200, json.dumps({"message": "Request Submitted"}))
    @api.response(400, json.dumps({"message": "Request couldn't process:"}))
    @api.response(500, json.dumps({"message": 'Failed to serve the request:'}))
    @api.expect(train_model_request_obj)
    def post(self):
        """
        train a model
        """
        run_response = {}
        try:
            body = request.json
            if body:
                unique_id = get_unique_id()
                trainer = Trainer(unique_id, body)
                sub_process = Process(target=trainer.train_model)
                sub_process.start()

                json_resp = {'message': 'Request submitted', 'processId': unique_id}

                logging.debug("Response : %s", json_resp)
                return Response(json.dumps(json_resp), 200)
            run_response['message'] = "couldn't process : " + str(body)
            run_response['status'] = json.dumps(ResponseStatus.DATA_ERROR)
            return Response(json.dumps(run_response), 400)
        except Exception as e:
            logging.exception(e)
            run_response['message'] = "Connector failed to serve the request : " + str(e)
            return Response(json.dumps(run_response), 500)


@api.route(BASE + API_VERSION + '/getStatus')
class RunOperation(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @api.response(200, json.dumps({"message": "Success"}))
    @api.response(400, json.dumps({"message": "Request couldn't process:"}))
    @api.response(500, json.dumps({"message": 'Failed to serve the request:'}))
    @api.expect(status_request_args)
    def get(self):
        """
        get status of a process
        """
        run_response = {}
        try:
            body = request.args
            if body:
                process_id = body['processId']
                response_obj = Data.get_process_status(process_id)

                logging.debug("Response : %s", response_obj)
                return Response(json.dumps(response_obj), 200)
            run_response['message'] = "couldn't process : " + str(body)
            run_response['status'] = json.dumps(ResponseStatus.DATA_ERROR)
            return Response(json.dumps(run_response), 400)
        except Exception as e:
            logging.exception(e)
            run_response['message'] = "Connector failed to serve the request : " + str(e)
            return Response(json.dumps(run_response), 500)


app.register_blueprint(blueprint)
