"""Create views for system end-points."""
import os
import pandas as pd
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_miscellaneous.storage import PumpWoodStorage
from pumpwood_djangoauth.system.models import KongService, KongRoute
from pumpwood_djangoauth.system.serializers import (
    KongServiceSerializer, KongRouteSerializer)
from pumpwood_djangoauth.config import kong_api, microservice_no_login
from pumpwood_communication.exceptions import (
    exceptions_dict, PumpWoodException, PumpWoodWrongParameters)

from pumpwood_djangoauth.permissions import (
    PumpwoodIsAuthenticated, PumpwoodCanRetrieveFile)


@api_view(['GET'])
@permission_classes([PumpwoodIsAuthenticated])
def view__get_kong_routes(request):
    """Get kong routes."""
    return Response(kong_api.list_all_routes())


@api_view(['GET'])
@permission_classes([PumpwoodIsAuthenticated])
def view__get_registred_endpoints(request):
    """Filter end-point to expose to frontend."""
    # Check if it is to hide routes from list
    availability = request.GET.get('availability', 'front_avaiable')
    availability_list = None
    if availability == 'front_avaiable':
        availability_list = ['front_avaiable']
    elif availability == 'all':
        availability_list = [x[0] for x in KongRoute.AVAILABILITY_CHOICES]
    else:
        msg = "Availability [{availability}] not implemented"
        raise PumpWoodWrongParameters(
            msg, payload={"availability": availability})

    # Get all services
    all_sevices = KongService.objects.order_by(
        "order", "description").all()
    all_sevices_data = KongServiceSerializer(
        all_sevices, many=True,
        fields=[
            "pk", "model_class", "service_url", "service_name",
            "order", "service_kong_id", "description", "notes",
            "healthcheck_route", "dimensions", "icon", "route_set",
            "extra_info", "description__verbose", "notes__verbose",
            "route_set"]).data

    resp_services = []
    for service in all_sevices_data:
        # Check if routes shoulb be display at the frontend
        route_set = []
        for route in service["route_set"]:
            is_to_return = (
                route["route_type"] == "endpoint") and (
                route["availability"] in availability_list)
            if is_to_return:
                route_set.append(route)
        pd_route_set = pd.DataFrame(route_set)

        # Do not list services that does not have routes to be displayed
        if len(pd_route_set) != 0:
            pd_route_set = pd_route_set.sort_values(
                by=["order", "description"])
            service["route_set"] = pd_route_set.to_dict("records")
            resp_services.append(service)
    return Response(resp_services)


@api_view(['GET', 'POST'])
@permission_classes([PumpwoodIsAuthenticated])
def view__dummy_call(request):
    """Expose a dummy endpoint for testing."""
    return Response({
        "full_path": request.build_absolute_uri(),
        "method": request.method,
        "headers": dict(request.headers),
        "data": request.data
    })


@api_view(['POST'])
@permission_classes([PumpwoodIsAuthenticated])
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
    if type(exception_class) is not str:
        msg = "exception_class must be a str: %s" % str(type(exception_class))
        raise PumpWoodException(message=msg)
    if type(exception_deep) is not int:
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
        TempException = exceptions_dict.get(exception_class) # NOQA
        if TempException is None:
            msg = "Error class not implemented: %s" % exception_class
            raise PumpWoodException(message=msg, payload=request_data)
        raise TempException(
            message="This is a dummy raise!!", payload=request_data)


class RestKongRoute(PumpWoodRestService):
    """Rest for model KongRoute."""
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

    #######
    # GUI #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                "order", "availability", "route_type", "service_id",
                "route_name", "description", "notes", "dimensions"]
        }, {
            "name": "kong info",
            "fields": [
                "route_url", "route_name", "route_kong_id"]
        }, {
            "name": "extra_info",
            "fields": ['extra_info']
        }
    ]
    gui_readonly = [
        "route_type", "service_id", "route_name",
        "description", "notes", "dimensions", "route_url", "route_name",
        "route_kong_id", 'extra_info']
    gui_verbose_field = '{pk} | {route_name}'
    #######

    def save(self, request):
        """Super save to create route using class function."""
        request_data = request.data
        return Response(KongRoute.create_route(
            availability=request_data.get("availability"),
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
    """Rest end-point for KongService."""
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

    #######
    # GUI #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                "order", "service_name", "description", "notes", "description",
                "dimensions"]
        }, {
            "name": "routes",
            "fields": ["route_set"]
        }, {
            "name": "kong info",
            "fields": [
                "service_kong_id", "service_url", "healthcheck_route"]
        }, {
            "name": "extra_info",
            "fields": ['extra_info']
        }
    ]
    gui_readonly = ['extra_info', 'route_set']
    gui_verbose_field = '{pk} | {service_name}'
    #######

    def save(self, request):
        """Super save."""
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
    """Class to serve files using Pumpwood Storage Object.

    It checks for user authentication and serve files using streaming
    request.
    """

    def __init__(self, storage_object: PumpWoodStorage):
        """__init__.

        Args:
            storage_object (PumpWoodStorage):
                Pumpwood Storage object that will be used to retrieve
                files from storage.
        """
        self.storage_object = storage_object

    def as_view(self):
        """Return a view function using storage_object set on object."""

        @login_required
        @permission_classes([PumpwoodCanRetrieveFile])
        def download_from_storage_view(request, file_path):
            file_interator = self.storage_object.get_read_file_iterator(
                file_path)
            file_name = os.path.basename(file_path)
            content_disposition = 'attachment; filename="{}"'.format(
                file_name)
            return StreamingHttpResponse(file_interator, headers={
                'Content-Disposition': content_disposition})
        return download_from_storage_view
