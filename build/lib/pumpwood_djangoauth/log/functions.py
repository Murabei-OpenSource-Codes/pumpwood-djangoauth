"""Functions to log activity at rest APIs."""
import datetime
from loguru import logger
from pumpwood_communication.serializers import pumpJsonDump


def log_api_request(user_id: int, permission_check: str, request_method: str,
                    path: str, model_class: str, end_point: str,
                    first_arg: str, second_arg: str, payload: str,
                    ingress_request: str = '') -> dict:
    """Log API request using a RabbitMQ queue, if rabbitmq_api is not None.

    RabbitMQ queue will be consumed by a worker, that may latter save
    information for audit.

    If rabbitmq_api is not set, logs will be sent to STDOUT with prefix,
    ## api_request_log ## .

    Args:
        user_id (int):
            ID of the logged user reponsible for the request.
        permission_check (str):
            Result of the permission check of the user.
        request_method (str):
            Method used on request, POST, GET, DELETE, ...
        path (str):
            Full request path.
        model_class (str):
            Model class associated with request.
        end_point (str):
            End-point used at the call, ex: retrieve, list,
            delete, save, retrieve-file, ...
        first_arg (str):
            First argument of the end-point.
        second_arg (str):
            Second argument of the end-point.
        payload (str): Payload of POST request, it will be limited to 300
            characters avoiding overload during database uploads.
        ingress_request (str):
            Log if call came througth ingress or was cluster internal.

    Returns:
        Return the dictionary that will be passed to RabbitMQ.
    """
    log_time = datetime.datetime.now(datetime.UTC).isoformat()
    log_dict = {
        'user_id': user_id,
        'permission_check': str(permission_check or '').lower(),
        'request_method': str(request_method or '').lower(),
        'path': str(path or '').lower(),
        'model_class': str(model_class or '').lower(),
        'end_point': (end_point or '').lower(),
        'first_arg': str(first_arg or '').lower(),
        'second_arg': str(second_arg or '').lower(),
        'ingress_request': str(ingress_request or '').lower()}
    log_dict_str = pumpJsonDump(log_dict).decode('utf-8')

    log_template = "{time} | api_request | {log_dict}".format(
        time=log_time, log_dict=log_dict_str)
    logger.opt(raw=True).info(log_template)
    return None
