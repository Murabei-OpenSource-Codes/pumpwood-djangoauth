"""
Define custom Pumpwood exception handler for Django.

Pumpwood exception handler will automatically treat PumpWoodException
raises that will be transformed to correct json response with associated
`status_code`.
"""

from rest_framework.views import exception_handler
from pumpwood_communication.exceptions import (
    PumpWoodException, PumpWoodObjectDoesNotExist, PumpWoodQueryException,
    PumpWoodUnauthorized)
from rest_framework.response import Response
from django.core.exceptions import (
    FieldError, ObjectDoesNotExist, PermissionDenied)


def custom_exception_handler(exc, context) -> Response:
    """
    Return response for exceptions raised on Pumpwood.

    Custom exception handler to treat Pumpwood exceptions and return
    exception payload as json.

    Some django errors will be mapped to PumpWoodException:
    - FieldError -> PumpWoodQueryException
    - ObjectDoesNotExist -> PumpWoodObjectDoesNotExist
    - PermissionDenied -> PumpWoodUnauthorized

    Args:
        exc [Exception]: Exception raised at request processing.
        context: Django rest framework context request.
    Returns:
        Returns the response with treated exception. Response will have
        status_code associated with PumpWoodException and payload with
        keys:
        - **payload [dict]:** Error payload associated with raise at
            PumpWoodException class.
        - **type [str]:** Returns the exception type string. Ex.:
            PumpWoodException, PumpWoodDataLoadingException,
            PumpWoodDatabaseError, PumpWoodDataTransformationException, ...
        - **message_not_fmt [str]:** Base message to be formated with payload
            data. Ex.: 'Object [{pk}] not found' message_not_fmt with payload
            `{"pk": 10, "other_message": "nice_error"}` will result `message`
            'Object [10] not found'.
        - **message [str]:** `message_not_fmt` formated message using payload
            dictionary information.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    if issubclass(type(exc), PumpWoodException):
        payload = exc.to_dict()
        return Response(
            payload, status=exc.status_code)

    if issubclass(type(exc), FieldError):
        pump_exc = PumpWoodQueryException(message=str(exc))
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), ObjectDoesNotExist):
        pump_exc = PumpWoodObjectDoesNotExist(message=str(exc))
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    if issubclass(type(exc), PermissionDenied):
        pump_exc = PumpWoodUnauthorized(message=str(exc))
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

    response = exception_handler(exc, context)
    return response
