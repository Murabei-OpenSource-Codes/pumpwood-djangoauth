"""Functions to log activity at rest APIs."""
import datetime
from loguru import logger
from pumpwood_communication.serializers import pumpJsonDump


def log_api_request(user_id: int, permission_check: str, request_method: str,
                    path: str, model_class: str, end_point: str,
                    first_arg: str, second_arg: str, ingress_request: str = '',
                    payload: str = '') -> None:
    """Write an API request audit line to stdout via loguru.

    Args:
        user_id (int):
            ID of the user responsible for the request.
        permission_check (str):
            Result of the permission check for the user.
        request_method (str):
            HTTP method used on the request, for example POST or GET.
        path (str):
            Full request path.
        model_class (str):
            Model class associated with the request.
        end_point (str):
            Endpoint action, for example retrieve, list, or save.
        first_arg (str):
            First path argument for the endpoint.
        second_arg (str):
            Second path argument for the endpoint.
        ingress_request (str):
            Whether the call came through ingress or was cluster-internal.
        payload (str):
            POST body snippet; callers should truncate to avoid large logs.

    Returns:
        None:
            Logging is side-effect only; nothing is returned.
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
