import logging
import os
import pickle
import traceback
from datetime import datetime
from typing import List, Tuple
from urllib.request import urlretrieve

import numpy as np
import pandas as pd
from autosklearn.estimators import AutoSklearnClassifier, AutoSklearnRegressor, AutoSklearnEstimator
from scipy.io import arff

from app.apis.data import Data
from config import TEMP_FOLDER


class Trainer:
    """
    This class train a model on a given data
    """

    def __init__(self, model_id, args) -> None:
        self.model_id = model_id
        self.__temp_dir = self.__get_temp_dir()
        self.__args = args

    def __log_info(self, message):
        logging.info(f"{self.model_id} : {datetime.now()}:: {message}")

    def __log_error(self, message):
        logging.error(f"{self.model_id} : {datetime.now()}:: {message}")

    def __log_debug(self, message):
        logging.debug(f"{self.model_id} : {datetime.now()}:: {message}")

    def __get_dir(self, parent: str, child: str) -> str:
        """
        Get a directory path from it's parent. This method create the directory if not present
        :param parent: parent directory
        :param child: child directory
        :return:
        """
        dir_path = os.path.join(parent, child)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    def __get_temp_dir(self) -> str:
        """
        Get temp dir where all the file will be created for this model
        :return:temp directory path
        """
        return self.__get_dir(TEMP_FOLDER, self.model_id)

    def __save_data_to_file(self, data_url: str, data_type: str) -> str:
        """
        save training data to file
        :param data_url: training data URL
        :param data_type: data type CSV or ARFF
        :return: saved file path
        """
        self.__log_info("saving data from url to file")

        data_dir = self.__get_dir(self.__temp_dir, 'data')
        file_save_path = os.path.join(data_dir, f"file.{data_type.lower()}")
        urlretrieve(data_url, file_save_path)
        return file_save_path

    def __load_data(self, data_path: str, data_type: str) -> pd.DataFrame:
        """
        Loda data into a pandas data frame
        :param data_path:
        :param data_type:
        :return: pandas data frame
        """
        self.__log_info("loading model")
        if data_type == "CSV":
            df = pd.read_csv(data_path)
        elif data_type == "ARFF":
            data = arff.loadarff(data_path)
            df = pd.DataFrame(data[0])
        else:
            raise Exception(f"{data_type} is not a supported data type")
        return df

    def __get_feature_target_values(self, data_path: str, data_type: str, target_field: str,
                                    ignore_columns: List[str], model_type: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get feature and target values a array
        :param data_path: data to load
        :param data_type: data type
        :param target_field: target column name
        :param ignore_columns: ignore column list
        :param model_type: model type CLASSIFICATION or REGRESSION
        :return:
        """
        self.__log_info("getting feature and target data")

        df = self.__load_data(data_path, data_type)
        if model_type == 'CLASSIFICATION':
            df[target_field] = df[target_field].astype(str)
        all_columns = list(df.columns)

        feature_columns = all_columns.copy()
        feature_columns.remove(target_field)
        if len(ignore_columns) > 0:
            for column in ignore_columns:
                feature_columns.remove(column)
        df = df.dropna(subset=feature_columns + [target_field])
        X = df[feature_columns].values
        y = df[target_field].values
        return X, y

    def __create_model(self, model_type: str, model_config: dict):
        """
        Create auto-sklearn model object
        :param model_type: model type CLASSIFICATION or REGRESSION
        :param model_config: model configuration
        :return:
        """
        self.__log_info("creating model object")

        model_temp_dir = os.path.join(self.__temp_dir, "model_temp")

        total_time = model_config['totalTime']
        time_per_run = model_config['timePerRun']
        memory_limit = model_config['memoryLimit']

        if model_type == "CLASSIFICATION":
            model = AutoSklearnClassifier(
                time_left_for_this_task=total_time,
                memory_limit=memory_limit,
                per_run_time_limit=time_per_run,
                delete_tmp_folder_after_terminate=False,
                ensemble_size=0,
                tmp_folder=model_temp_dir
            )

        elif model_type == "REGRESSION":
            model = AutoSklearnRegressor(
                time_left_for_this_task=total_time,
                memory_limit=memory_limit,
                per_run_time_limit=time_per_run,
                delete_tmp_folder_after_terminate=True,
                ensemble_size=model_config.get('ensembleSize', 50),
                ensemble_nbest=model_config.get('ensembleSize', 50),
                max_models_on_disc=model_config.get('ensembleSize', 50),
            )

        else:
            raise Exception(f"{model_type} not a valid model type")
        return model

    def __save_model(self, model: AutoSklearnEstimator) -> str:
        """
        Save model to file
        :param model:save model path
        :return:
        """
        self.__log_info("saving model to file")

        model_file_path = os.path.join(self.__temp_dir, "model.pkl")
        pickle.dump(model, open(model_file_path, 'wb'))
        return model_file_path

    def train_model(self) -> None:
        try:
            Data.add_process(self.model_id, "RUNNING")
            self.__log_info("process started")

            data_config = self.__args['data']
            training_data_url = data_config['trainingData']
            data_type = data_config['dataType']
            data_path = self.__save_data_to_file(training_data_url, data_type)

            target_field = data_config['targetField']
            model_type = data_config['modelType']
            ignore_columns = data_config.get('ignoreColumns', [])

            model_config = self.__args['modelConfig']

            X, y = self.__get_feature_target_values(data_path, data_type, target_field, ignore_columns, model_type)
            model = self.__create_model(model_type, model_config)

            self.__log_info("model fit started")
            model.fit(X.copy(), y.copy())

            self.__log_info("model fit ensemble")
            model.fit_ensemble(y.copy(), ensemble_size=model_config.get("ensembleSize", 50))

            self.__save_model(model)
            self.__log_info("process completed")
            Data.add_process(self.model_id, "COMPLETED")
        except Exception as e:
            exception_message = traceback.format_exc()
            self.__log_error(exception_message)
            Data.add_process(self.model_id, "FAILED", exception_message)
