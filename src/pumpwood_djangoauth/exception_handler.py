"""Define custom exception handlers for Pumpwood systems.

Custom errors can be used to treat Pumpwood exceptions and return a JSON
payload with a non-2XX status code.

``custom_exception_handler`` can be registered in the Django
``REST_FRAMEWORK`` settings dictionary.

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'knox.auth.TokenAuthentication',
    ),
    'EXCEPTION_HANDLER': (
        # Add custom handler for API Calls
        'pumpwood_djangoauth.exception_handler.custom_exception_handler'
    )
}
```
"""
from django.conf import settings
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, DatabaseError
from rest_framework.response import Response
from rest_framework.exceptions import (
    ParseError, AuthenticationFailed, NotAuthenticated,
    PermissionDenied, NotFound, MethodNotAllowed, NotAcceptable,
    ValidationError)
from pumpwood_communication.exceptions import (
    PumpWoodException, PumpWoodObjectDoesNotExist, PumpWoodQueryException,
    PumpWoodUnauthorized, PumpWoodIntegrityError, PumpWoodWrongParameters,
    PumpWoodForbidden, PumpWoodObjectSavingException)
from pumpwood_miscellaneous.error import log_error
from pumpwood_database_error.psycopg2_error import TreatPsycopg2Error


def _create_sqlachemy_str(django_db_dict: dict) -> str:
    """Build a PostgreSQL SQLAlchemy connection URL from Django settings.

    Args:
        django_db_dict (dict):
            Django ``DATABASES`` mapping; the ``default`` entry is used.

    Returns:
        str:
            SQLAlchemy connection URL for PostgreSQL.
    """
    connection_string = (
    "postgresql://{user}:{password}@{host}:{port}/{name}")\
        .format(
            user=django_db_dict['default']['USER'],
            password=django_db_dict['default']['PASSWORD'],
            host=django_db_dict['default']['HOST'],
            port=django_db_dict['default']['PORT'],
            name=django_db_dict['default']['NAME'])
    return connection_string


def custom_exception_handler(exc, context) -> Response | None:
    """Map Django, DRF, and PumpWood exceptions to API error responses.

    Args:
        exc (Exception):
            Exception raised while processing the request.
        context (dict):
            DRF exception context with ``view`` and ``request`` keys.

    Returns:
        Response | None:
            ``Response`` with serialized PumpWood error payload and matching
            HTTP status when the exception is handled; otherwise the result
            of DRF's default ``exception_handler``, which may be ``None``.
    """
    from rest_framework.views import exception_handler

    log_error(exc=exc)

    ##########################################################
    # Call REST framework's default exception handler first, #
    # to get the standard error response.
    # Django errors
    pump_exc = None
    payload = None
    if issubclass(type(exc), django_exceptions.FieldError):
        pump_exc = PumpWoodQueryException(message=str(exc))
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), django_exceptions.ObjectDoesNotExist):
        pump_exc = PumpWoodObjectDoesNotExist(message=str(exc))
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), django_exceptions.PermissionDenied):
        pump_exc = PumpWoodUnauthorized(message=str(exc))
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    # Django database error
    if issubclass(type(exc), DatabaseError):
        pg_exception = exc.__cause__
        connection_url = _create_sqlachemy_str(
            django_db_dict=settings.DATABASES)
        payload = TreatPsycopg2Error.treat(
            error=pg_exception, connection_url=connection_url)
        status_code = payload.get('status_code', 400)
        return Response(payload, status=status_code)

    #########################
    # Rest framework errors #
    if issubclass(type(exc), ParseError):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodWrongParameters(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=exc.status_code)

    if issubclass(type(exc), AuthenticationFailed):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodUnauthorized(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), NotAuthenticated):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodUnauthorized(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), PermissionDenied):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodForbidden(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), NotFound):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodObjectDoesNotExist(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), MethodNotAllowed):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodForbidden(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), NotAcceptable):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodForbidden(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), ValidationError):
        full_details = exc.get_full_details()
        message_list = []
        msg_template = "[key] {message}"
        for key, item in full_details.items():
            message_list.append(msg_template.format(
                key=key, message=item['message']))
        message = '\n'.join(message_list)
        pump_exc = PumpWoodObjectSavingException(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    ######################################################################
    # Treat Pumpwood Exceptions and return the serialized information on a
    # dictonary with correct status_code
    if issubclass(type(exc), PumpWoodException):
        pump_exc = exc
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    response = exception_handler(exc, context)
    return response
