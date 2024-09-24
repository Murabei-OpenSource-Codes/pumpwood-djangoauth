"""
Define custom exception handlers for Pumpwood systems.

Custom erros can be used to correctly treat Pumpwood Exceptions and return
the treated erro as a JSON with not 2XX status code.

`custom_exception_handler` can be used at REST_FRAMEWORK MiddleWare at Django.

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
        'pumpwood_djangoviews.exception_handler.custom_exception_handler'
    )
}
```
"""
from django.core import exceptions as django_exceptions
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework.exceptions import (
    ParseError, AuthenticationFailed, NotAuthenticated,
    PermissionDenied, NotFound, MethodNotAllowed, NotAcceptable,
    ValidationError)
from pumpwood_communication.exceptions import (
    PumpWoodException, PumpWoodObjectDoesNotExist, PumpWoodQueryException,
    PumpWoodUnauthorized, PumpWoodIntegrityError, PumpWoodWrongParameters,
    PumpWoodForbidden, PumpWoodObjectSavingException)


def custom_exception_handler(exc, context) -> Response:
    """
    Treat custom exception handler to PumpWoodExceptions.

    Args:
        exc [Exception]:
            Exception raised processing request.
        context:
            Context of the error that was raised.
    Returns:
        Return a response with error code depending of the PumpWoodException
        raised. It returns a serialized dictionary with exception data.
    """
    from rest_framework.views import exception_handler

    ##########################################################
    # Call REST framework's default exception handler first, #
    # to get the standard error response.
    # Django errors
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
    if issubclass(type(exc), IntegrityError):
        pump_exc = PumpWoodIntegrityError(message=str(exc))
        payload = pump_exc.to_dict()
        return Response(
            payload, status=pump_exc.status_code)

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
            payload, status=exc.status_code)

    if issubclass(type(exc), NotAuthenticated):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodUnauthorized(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=exc.status_code)

    if issubclass(type(exc), PermissionDenied):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodForbidden(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=exc.status_code)

    if issubclass(type(exc), NotFound):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodObjectDoesNotExist(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=exc.status_code)

    if issubclass(type(exc), MethodNotAllowed):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodForbidden(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=exc.status_code)

    if issubclass(type(exc), NotAcceptable):
        full_details = exc.get_full_details()
        message = full_details.pop('message')
        pump_exc = PumpWoodForbidden(
            message=message, payload=full_details)
        payload = pump_exc.to_dict()
        return Response(
            payload, status=exc.status_code)

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
            payload, status=exc.status_code)

    ######################################################################
    # Treat Pumpwood Exceptions and return the serialized information on a
    # dictonary with correct status_code
    if issubclass(type(exc), PumpWoodException):
        payload = exc.to_dict()
        return Response(
            payload, status=exc.status_code)

    response = exception_handler(exc, context)
    return response
