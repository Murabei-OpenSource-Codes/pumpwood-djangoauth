"""Manage Kong routes for Pumpwood."""
from django.db import models
from django.db.models import Q
from pumpwood_djangoviews.action import action
from pumpwood_djangoauth.kong.singleton import kong_api
from pumpwood_communication import exceptions
from pumpwood_communication.serializers import PumpWoodJSONEncoder


class KongService(models.Model):
    """Services Registered at Kong API Gateway."""

    service_url = models.CharField(
        null=False, max_length=100, unique=True,
        help_text="service url to redirect the http calls.")
    service_name = models.TextField(
        null=False, max_length=100, unique=True,
        help_text="name of the service (must be unique).")
    service_kong_id = models.TextField(
        null=False, unique=True,
        help_text="id of the service on kong.")
    description = models.TextField(
        null=False, unique=True,
        help_text="short description for the service (must be unique).")
    notes = models.TextField(
        null=False, default="", blank=True,
        help_text="long description for the service.")
    healthcheck_route = models.TextField(
        null=True, unique=True,
        help_text="path to health check if the service is avaiable.")
    dimentions = models.JSONField(
        default=dict, help_text="dictionary of tags to help organization",
        encoder=PumpWoodJSONEncoder)
    icon = models.TextField(
        null=True, blank=True, help_text="icon to be used on front-end.")
    extra_info = models.JSONField(
        default=dict, blank=True,
        help_text="other information that can be usefull for this service",
        encoder=PumpWoodJSONEncoder)

    def __str__(self):
        return 'microservice: %s; endpoint: %s' % (
            self.service_name, self.service_url)

    class Meta:
        db_table = 'pumpwood__service'

    @classmethod
    @action(info='Load service/routes on Kong.')
    def load_kong_service(cls, list_service_id: list = None) -> bool:
        """
        Load kong services and routes.

        Load services and routes in database at Kong. This action does not
        remove other kongs end-points.

        Args
            No Args.
        Kwargs:
            list_service_id [list]: List of ids to reload routes on Kong.
        Return [bool]:
            Return true.
        """
        services = None
        if list_service_id:
            services = cls.objects.filter(id__in=list_service_id)
        else:
            services = cls.objects.all()

        for s in services:
            cls.create_service(
                service_url=s.service_url,
                service_name=s.service_name,
                description=s.description,
                notes=s.notes,
                icon=s.icon,
                healthcheck_route=s.healthcheck_route,
                dimentions=s.dimentions,
                extra_info=s.extra_info)

            for r in s.route_set.all():
                KongRoute.create_route(
                    service_id=r.service_id,
                    route_url=r.route_url,
                    route_name=r.route_name,
                    route_type=r.route_type,
                    description=r.description,
                    notes=r.notes,
                    icon=r.icon,
                    dimentions=r.dimentions,
                    extra_info=r.extra_info)
        return True

    @classmethod
    @action(info='Delete services/routes and reload them on Kong.')
    def reload_kong_service(cls, list_service_id: list = None) -> bool:
        """
        Reload kong services, a small down time may occur.

        Remove and recreate all services and kong routes if list_service_id
        not passed as argument.

        Args
            No Args.
        Kwargs:
            list_service_id [list]: List of ids to reload routes on Kong.
        Return [bool]:
            Return true.
        """
        list_kong_service_ids = None
        if list_service_id:
            services = cls.objects.filter(id__in=list_service_id)
            list_kong_service_ids = [s.service_kong_id for s in services]
        else:
            services = cls.objects.all()

        try:
            kong_api.delete_routes_and_service(
                list_service_id=list_kong_service_ids)
        except Exception as e:
            message = (
                "Error cleaning Kong's services and routes, some services "
                "may have lost it's routing. Exception:\n{}").format(str(e))
            raise exceptions.PumpWoodException(message=message)

        cls.load_kong_service(list_service_id=list_service_id)
        return True

    @classmethod
    @action(info='Create a Kong service.')
    def create_service(cls, service_url: str, service_name: str,
                       description: str, notes: str, icon: str = None,
                       healthcheck_route: str = None,
                       dimentions: dict = {}, extra_info: dict = {}) -> dict:
        """
        Create a Kong service to redirect calls.

        Save calls use same object to create or patch already created object.

        Args:
            service_url [str]: URL of the service to which call to this service
                will be redicted as is.
            service_name [str]: Unique name for the service
            description [str]: Unique description for the service.
            notes [str]: A long description for the service.
        Kwargs:
            healthcheck_route [str] = None: A health check end-point for the
                service.
            dimentions [dict] = {}: A dimentions for the service to help
                quering.
            extra_info [dict] = {}: Extra information to be saved with service.
            icon [str] = None: An icon associated with the service.
        Returns [dict] -> dict:
            Return a serialized KongService object.
        """
        from pumpwood_djangoauth.system.serializers import (
            KongServiceSerializer)
        registred_service = KongService.objects.filter(
            Q(service_name=service_name) | Q(service_url=service_url)
        ).first()

        service_return = kong_api.register_service(
            service_name=service_name, service_url=service_url,
            healthcheck_route=healthcheck_route)
        extra_info["kong_data"] = service_return
        service_kong_id = service_return["id"]

        if registred_service is None:
            registred_service = KongService(
                service_url=service_url,
                service_name=service_name,
                service_kong_id=service_kong_id,
                description=description,
                notes=notes,
                healthcheck_route=healthcheck_route,
                dimentions=dimentions,
                icon=icon,
                extra_info=extra_info)
            registred_service.save()
        else:
            registred_service.service_url = service_url
            registred_service.service_name = service_name
            registred_service.service_kong_id = service_kong_id
            registred_service.description = description
            registred_service.notes = notes
            registred_service.healthcheck_route = healthcheck_route
            registred_service.dimentions = dimentions
            registred_service.icon = icon
            registred_service.extra_info = extra_info
            registred_service.save()
        return KongServiceSerializer(registred_service, many=False).data


class KongRoute(models.Model):
    """Routes registred on Kong API Gateway."""

    ROUTE_TYPES = [
        ('endpoint', 'Object End-Point'),
        ('aux', 'Auxiliar End-Point'),
        ('gui', 'User Interface'),
        ('static', 'Static Files'),
        ('admin', 'Admin site')]

    service = models.ForeignKey(
        KongService, on_delete=models.CASCADE, related_name="route_set",
        help_text="service associated with the route.")
    route_url = models.CharField(
        null=False, max_length=100, unique=True,
        help_text="service associated with the route (must be unique).")
    route_name = models.CharField(
        null=False, max_length=100, unique=True,
        help_text="name of the route (must be unique).")
    route_kong_id = models.TextField(
        null=False, unique=True,
        help_text="route identification on Kong")
    route_type = models.CharField(
        max_length=10, choices=ROUTE_TYPES,
        help_text="type of the route [endpoint, aux, gui, static, admin]")

    description = models.TextField(
        null=False, unique=True,
        help_text="a short description of the route.")
    notes = models.TextField(
        null=False, default="", blank=True,
        help_text="a long description of the route.")
    dimentions = models.JSONField(
        default=dict, help_text="dictionary of tags to help organization",
        encoder=PumpWoodJSONEncoder)
    icon = models.TextField(
        null=True, blank=True,
        help_text="icon to be used on front-end.")
    extra_info = models.JSONField(
        default=dict, blank=True,
        help_text="other information that can be usefull for this route",
        encoder=PumpWoodJSONEncoder)

    class Meta:
        db_table = 'pumpwood__route'
        unique_together = [['service', 'route_name']]

    def __str__(self):
        return 'service: %s; route: %s; route name: %s' % (
            self.service.service_name, self.route_name, self.route_url)

    @classmethod
    @action(info='Create a Kong route.')
    def create_route(cls, service_id: int, route_url: str, route_name: str,
                     route_type: str, description: str, notes: str,
                     icon: str = None, strip_path: bool = False,
                     dimentions: dict = {}, extra_info: dict = {}) -> dict:
        """
        Create a Kong route to redirect calls.

        Save calls use same object to create or patch already created object.

        Args:
            service_id [int]: Id of the service associated with route on
                PumpWood.
            route_url [str]: Route URL to redirect the calls to service.
            route_name [str]: Unique name for the route.
            route_type [str]: Type of the route to create values must be in:
                ['endpoint', 'aux', 'gui', 'static', 'admin']
            description [str]: Unique description for the service.
            notes [str]: A long description for the service.
        Kwargs:
            strip_path [bool]: If kong will strip path when routing downstream.
            icon [str] = None: An icon associated with the service.
            dimentions [dict] = {}: A dimentions for the service to help
                quering.
            extra_info [dict] = {}: Extra information to be saved with
                service.
        Returns [dict]:
            Return a serialized KongRoute object.
        """
        from pumpwood_djangoauth.system.serializers import (
            KongRouteSerializer)

        # Check values for route_type
        possible_types = [x[0] for x in cls.ROUTE_TYPES]
        if route_type not in possible_types:
            msg = "route_type must be in %s" % str(possible_types)
            raise exceptions.PumpWoodActionArgsException(
                message=msg, payload={"route_type": msg})

        registred_route = KongRoute.objects.filter(
            Q(route_name=route_name) | Q(route_url=route_url)
        ).first()

        service_object = KongService.objects.get(id=service_id)
        route_return = kong_api.register_route(
            service_id=service_object.service_kong_id,
            route_name=route_name, route_url=route_url,
            strip_path=strip_path)
        extra_info["kong_data"] = route_return

        if registred_route is None:
            registred_route = KongRoute(
                service_id=service_object.id,
                route_url=route_url,
                route_name=route_name,
                route_kong_id=route_return["id"],
                route_type=route_type,
                description=description,
                notes=notes,
                icon=icon,
                dimentions=dimentions,
                extra_info=extra_info)
            registred_route.save()
        else:
            registred_route.service_id = service_object.id
            registred_route.route_url = route_url
            registred_route.route_name = route_name
            registred_route.route_kong_id = route_return["id"]
            registred_route.route_type = route_type
            registred_route.description = description
            registred_route.notes = notes
            registred_route.icon = icon
            registred_route.dimentions = dimentions
            registred_route.extra_info = extra_info
            registred_route.save()
        return KongRouteSerializer(registred_route, many=False).data
