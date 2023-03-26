"""Create views for system end-points."""
import os
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.system.models import KongService, KongRoute
from pumpwood_djangoauth.system.serializers import (
    KongServiceSerializer, KongRouteSerializer)
from pumpwood_djangoauth.config import kong_api, microservice_no_login
from pumpwood_communication.exceptions import (
    exceptions_dict, PumpWoodException)


@api_view(['GET'])
def view__get_kong_routes(request):
    """Get kong routes."""
    return Response(kong_api.list_all_routes())


@api_view(['GET'])
def view__get_registred_endpoints(request):
    """Filter end-point to expose to frontend."""
    all_sevices = KongService.objects.order_by("description").all()
    all_sevices_data = KongServiceSerializer(
        all_sevices, many=True).data

    resp_services = []
    for x in all_sevices_data:
        x["route_set"] = [
            route for route in x["route_set"]
            if route["route_type"] == "endpoint"]
        if len(x["route_set"]) != 0:
            resp_services.append(x)
    return Response(resp_services)


@api_view(['GET', 'POST'])
def view__dummy_call(request):
    """Expose a dummy endpoint for testing."""
    return Response({
        "full_path": request.build_absolute_uri(),
        "method": request.method,
        "headers": request.headers,
        "data": request.data
    })


@api_view(['POST'])
def view__dummy_raise(request):
    """End-point to test error handling in Pumpwood."""
    # Get auth header for recursive error test
    auth_header = {
        "Authorization": request.headers.get("Authorization")
    }

    request_data = request.data
    exception_deep = request_data.get("exception_deep")
    exception_class = request_data.get("exception_class")

    # Checking if data is with the correct type
    if not type(exception_class) == str:
        msg = "exception_class must be a str: %s" % str(type(exception_class))
        raise PumpWoodException(message=msg)
    if not type(exception_deep) == int:
        msg = "exception_deep must be a int: %s" % str(type(exception_deep))
        raise PumpWoodException(message=msg)
    if 3 < exception_deep:
        msg = "exception_deep <= 3: %s" % str(exception_deep)
        raise PumpWoodException(message=msg)

    if 1 < exception_deep:
        microservice_no_login.dummy_raise(
            exception_class=exception_class,
            exception_deep=exception_deep - 1,
            auth_header=auth_header)
    elif exception_class == "ServerError":
        # Raise a simple server error
        raise Exception("Server error my friend!")
    else:
        TempException = exceptions_dict.get(exception_class)
        if TempException is None:
            msg = "Error class not implemented: %s" % exception_class
            raise PumpWoodException(message=msg, payload=request_data)
        raise TempException(
            message="This is a dummy raise!!", payload=request_data)


class RestKongRoute(PumpWoodRestService):
    endpoint_description = "Kong Route"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "kong",
        "sub_type": "service",
    }
    icon = None

    service_model = KongRoute
    serializer = KongRouteSerializer
    list_fields = [
        "pk", "model_class", "service_id", "route_name", "route_type",
        "description", "icon"]
    foreign_keys = {
        'service_id': {'model_class': 'KongService', 'many': False}
    }

    def save(self, request):
        request_data = request.data
        return Response(KongRoute.create_route(
            service_id=request_data["service_id"],
            route_url=request_data["route_url"],
            route_name=request_data["route_name"],
            route_type=request_data["route_type"],
            description=request_data["description"],
            notes=request_data["notes"],
            icon=request_data.get("icon", None),
            dimensions=request_data.get("dimensions", {}),
            extra_info=request_data.get("extra_info", {})))


class RestKongService(PumpWoodRestService):
    endpoint_description = "Kong Services"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "kong",
        "sub_type": "service",
    }
    icon = None

    service_model = KongService
    serializer = KongServiceSerializer

    list_fields = [
        "pk", "model_class", "service_name", "service_kong_id",
        "description", "icon"]
    foreign_keys = {
        'route_set': {'model_class': 'KongRoute', 'many': True}
    }

    def save(self, request):
        request_data = request.data
        return Response(KongService.create_service(
            service_url=request_data["service_url"],
            service_name=request_data["service_name"],
            description=request_data["description"],
            notes=request_data["notes"],
            icon=request_data.get("icon", None),
            healthcheck_route=request_data.get(
                "healthcheck_route", None),
            dimensions=request_data.get("dimensions", {}),
            extra_info=request_data.get("extra_info", {})))


class ServeMediaFiles:
    """
    Class to serve files using Pumpwood Storage Object and checking user
    authentication.
    """

    def __init__(self, storage_object):
        self.storage_object = storage_object

    def as_view(self):
        """Return a view function using storage_object set on object."""
        @login_required
        def download_from_storage_view(request, file_path):
            file_interator = self.storage_object.get_read_file_iterator(
                file_path)
            file_name = os.path.basename(file_path)
            content_disposition = 'attachment; filename="{}"'.format(
                file_name)
            return StreamingHttpResponse(file_interator, headers={
                'Content-Disposition': content_disposition})
        return download_from_storage_view
