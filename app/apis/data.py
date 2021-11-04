import json
from datetime import datetime
from os import path

from app.core.C import DATETIME_FORMAT
from config import TEMP_FOLDER


class Data:
    """
    This is static class contains data about process status
    """

    @staticmethod
    def get_process_status(process_id):
        process_info = Data.get_process_status_json(process_id)
        response = {}
        if process_info is None:
            response['message'] = f"process id {process_id} not found"
        else:
            process_status = process_info['status']
            response['processStatus'] = process_status
            if process_status == 'FAILED':
                failure_reason = process_info['failureReason']
                response['failureReason'] = failure_reason

                started_at = datetime.strptime(process_info['started_at'], DATETIME_FORMAT)
                failed_at = datetime.strptime(process_info['failed_at'], DATETIME_FORMAT)
                failed_time = int((failed_at - started_at).total_seconds())
                response['timeInfo'] = f"process failed after {failed_time} seconds"
            elif process_status == 'COMPLETED':
                started_at = datetime.strptime(process_info['started_at'], DATETIME_FORMAT)
                completed_at = datetime.strptime(process_info['completed_at'], DATETIME_FORMAT)
                compilation_time = int((completed_at - started_at).total_seconds())
                response['timeInfo'] = f"compilation time {compilation_time} seconds"
            else:
                current_datetime = datetime.now()
                started_at = datetime.strptime(process_info['started_at'], DATETIME_FORMAT)
                running_for = int((current_datetime - started_at).total_seconds())
                response['timeInfo'] = f"running for {running_for} seconds"

        return response

    @staticmethod
    def add_process(process_id, status, status_info=""):
        process_info = Data.get_process_status_json(process_id)
        if process_info is None:
            process_info = {}

        process_info['status'] = status

        current_datetime = datetime.now().strftime(DATETIME_FORMAT)

        if status == 'FAILED':
            process_info['failureReason'] = status_info
            process_info['failed_at'] = current_datetime
        elif status == 'COMPLETED':
            process_info['completed_at'] = current_datetime
        else:
            process_info['started_at'] = current_datetime
        Data.save_process_status_json(process_id, process_info)

    @staticmethod
    def get_process_status_file(process_id):
        return path.join(TEMP_FOLDER, process_id, 'status.json')

    @staticmethod
    def get_process_status_json(process_id):
        process_file_path = Data.get_process_status_file(process_id)
        if path.exists(process_file_path):
            return json.load(open(process_file_path, 'r'))
        return None

    @staticmethod
    def save_process_status_json(process_id, status_json):
        process_file_path = Data.get_process_status_file(process_id)
        return json.dump(status_json, open(process_file_path, 'w'))
