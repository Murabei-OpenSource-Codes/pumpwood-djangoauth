"""Create views for system end-points."""
from rest_framework.response import Response
from rest_framework.decorators import api_view
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_django_auth.system.models import KongService, KongRoute
from pumpwood_django_auth.system.serializers import (
    KongServiceSerializer, KongRouteSerializer)
from pumpwood_django_auth.kong.singleton import kong_api
from pumpwood_communication import exceptions


@api_view(['GET'])
def view__get_kong_routes(request):
    """Get kong routes."""
    return Response(kong_api.list_all_routes())


@api_view(['GET'])
def view__get_registred_endpoints(request):
    """Filter end-point to expose to frontend."""
    all_sevices = KongService.objects.all()
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


class RestKongRoute(PumpWoodRestService):
    endpoint_description = "Kong Route"
    dimentions = {
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
        "pk", "model_class", "service_id", "route_url", "route_name",
        "route_kong_id", "route_type", "description", "notes", "dimentions",
        "icon"]
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
            dimentions=request_data.get("dimentions", {}),
            extra_info=request_data.get("extra_info", {})))


class RestKongService(PumpWoodRestService):
    endpoint_description = "Kong Services"
    dimentions = {
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
        "pk", "model_class", "service_url", "service_name", "service_kong_id",
        "description", "notes", "healthcheck_route", "dimentions", "icon",
        "route_set"]
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
            dimentions=request_data.get("dimentions", {}),
            extra_info=request_data.get("extra_info", {})))
