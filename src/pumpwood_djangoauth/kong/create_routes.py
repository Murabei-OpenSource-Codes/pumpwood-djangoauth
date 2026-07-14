"""Auxiliary module to create routes and services at Kong."""
import os
import textwrap
from copy import deepcopy
from slugify import slugify


def register_auth_kong_objects(service_url: str, service_description: str,
                               service_notes: str, service_name: str,
                               service_dimensions: dict,
                               healthcheck_route: str, routes: list = [],
                               viewsets: list = [], service_icon: str = None,
                               service_extra_info: dict = {}):
    """Register auth objects in Kong and persist them in the database.

    Args:
        service_url (str):
            Microservice endpoint URL.
        service_description (str):
            Short service description.
        service_name (str):
            Name of the service.
        service_notes (str):
            Long service description.
        service_dimensions (dict):
            Tag/value pairs used to organize services in the database.
        healthcheck_route (str):
            Health-check URL for the microservice.
        routes (list):
            Route definitions associated with the microservice.
        viewsets (list):
            Pumpwood view classes used to create model routes at Kong.
        service_icon (str):
            Icon associated with the service.
        service_extra_info (dict):
            Extra metadata saved with the service.
    """
    from django import db
    from django.core.wsgi import get_wsgi_application

    # Load apps before importing then to code
    db.connections.close_all()
    get_wsgi_application()
    from pumpwood_djangoauth.system.models import KongService, KongRoute

    ###########################
    # Get viewset information #
    temp_routes = deepcopy(routes)
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
                "list_fields": view.get_list_fields(),
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
            extra_info=route.get("extra_info", {}))
