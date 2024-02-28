"""Create routes and services."""
import os
import random
import time
import textwrap
from copy import deepcopy
from django.core.wsgi import get_wsgi_application
from slugify import slugify
from django import db


def register_auth_kong_objects(service_url: str, service_description: str,
                               service_notes: str, service_name: str,
                               service_dimensions: dict,
                               healthcheck_route: str, routes: list = [],
                               viewsets: list = [], service_icon: str = None,
                               service_extra_info: dict = {}):
    """
    Register auth objects in kong and add them to database.

    Args:
        service_url [str]: Microservice endpoint url.
        service_name [str]: Service name
        healthcheck_route [str]: Health-check url for the microservice.
        routes [list[dict]]: List of information to create routes associated
            with the microservice. Ex:
                {
                    "route_url": "/rest/kongroute/",
                    "route_name": "pumpwood-auth-app--kongroute",
                    "route_type": "endpoint",
                    "description": "Microservice Routes",
                    "strip_path": False,
                    "notes": (
                        "Routes registred on Pumpwood, each one is associated "
                        "with a microservice service."),
                    "dimensions": {
                        "microservice": "pumpwood-auth-app",
                        "service_type": "core",
                        "function": "system",
                        "endpoint": "kongroute",
                        "route_type": "endpoint"},
                    "icon": ""
                }, {  # Admin
                    "route_url": "/admin/pumpwood-auth-app/gui/",
                    "route_name": "pumpwood-auth-app--admin",
                    "route_type": "admin",
                    "description": "Pumpwood Auth Admin",
                    "notes": (
                        "Admin for pumpwood-auth-app microservice."),
                    "dimensions": {
                        "microservice": "pumpwood-auth-app",
                        "service_type": "core",
                        "function": "gui",
                        "route_type": "admin"},
                    "icon": ""
                }
    """
    # Load apps before importing then to code
    db.connections.close_all()
    get_wsgi_application()
    from pumpwood_djangoauth.system.models import KongService, KongRoute

    temp_routes = deepcopy(routes)
    sleep_time = random.uniform(0, 5)
    print("Slepping random time to not crash workers: ", sleep_time)
    time.sleep(sleep_time)

    ###########################
    # Get viewset information #
    for view in viewsets:
        model_class_name = view.service_model.__name__
        suffix = os.getenv('ENDPOINT_SUFFIX', '')
        model_class_name = slugify(suffix + model_class_name)
        route_url = "/rest/{model_class_name}/".format(
            model_class_name=model_class_name)

        description = view.endpoint_description
        notes = textwrap.dedent(
            getattr(view.service_model, "__doc__", "")).strip()
        dimensions = view.dimensions

        # Checking unique constraints
        unique_docs = ""
        unique_together = getattr(
            view.service_model._meta, "unique_together", [])
        for x in unique_together:
            unique_columns = ", ".join(x)
            if unique_docs == "":
                unique_docs += "\n\n- Unique Constraints:"
            unique_docs += "\n[" + unique_columns + "]"
        notes = notes + unique_docs

        # Search_options
        search_options = view.cls_fields_options()

        # Icon
        icon = view.icon
        temp_routes.append({
            "route_url": route_url,
            "route_name": model_class_name,
            "route_type": "endpoint",
            "description": description,
            "notes": notes,
            "dimensions": dimensions,
            "icon": icon,
            "extra_info": {
                "view_type": view._view_type,
                "foreign_keys": view.foreign_keys,
                "list_fields": view.list_fields,
                "file_fields": view.file_fields,
                "search_options": search_options
            }})

    # Create Service
    kong_service = KongService.create_service(
        service_url=service_url,
        service_name=service_name,
        description=service_description,
        notes=service_notes,
        healthcheck_route=healthcheck_route,
        dimensions=service_dimensions,
        icon=service_icon,
        extra_info=service_extra_info)

    # Create Routes
    for route in temp_routes:
        KongRoute.create_route(
            service_id=kong_service["pk"],
            route_url=route["route_url"],
            route_name=route["route_name"],
            route_type=route["route_type"],
            strip_path=route.get("strip_path", False),
            description=route["description"],
            notes=route["notes"],
            dimensions=route["dimensions"],
            icon=route["icon"],
            extra_info=route["extra_info"])
