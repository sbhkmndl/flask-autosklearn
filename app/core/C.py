import uuid

DATETIME_FORMAT = "%y-%m-%d %H:%M:%S"


def get_unique_id():
    return str(uuid.uuid4())
