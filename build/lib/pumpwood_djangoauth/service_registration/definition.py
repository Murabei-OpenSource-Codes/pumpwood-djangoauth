"""Default service and routes definition for auth app.

Create dict setting Pumpwood Auth default services and routes.
"""
import os
from pumpwood_djangoauth.config import MEDIA_URL


_service_url = os.environ.get("SERVICE_URL")
_auth_static_service = os.environ.get("AUTH_STATIC_SERVICE")


def get_service_definitions():
    """Function to generate service definition."""
    from pumpwood_djangoauth.system.views import (
        RestKongRoute, RestKongService)
    from pumpwood_djangoauth.registration.views import (
        RestUser, RestUserProfile)
    from pumpwood_djangoauth.metabase.views import (
        RestMetabaseDashboard, RestMetabaseDashboardParameter)
    from pumpwood_djangoauth.i8n.views import RestPumpwoodI8nTranslation
    from pumpwood_djangoauth.api_permission.views import (
        RestPumpwoodPermissionPolicy, RestPumpwoodPermissionPolicyAction,
        RestPumpwoodPermissionPolicyGroupM2M,
        RestPumpwoodPermissionPolicyUserM2M)
    from pumpwood_djangoauth.row_permission.views import (
        RestPumpwoodRowPermission, RestPumpwoodRowPermissionGroupM2M,
        RestPumpwoodRowPermissionUserM2M)
    from pumpwood_djangoauth.groups.views import (
        RestPumpwoodUserGroup, RestPumpwoodUserGroupM2M)

    # Local Models
    from fixtures.views import RestFixturesRowLevelPermission

    auth_service_definition = {
        "service_url": _service_url,
        "service_name": "pumpwood-auth-app",
        "healthcheck_route": "/health-check/pumpwood-auth-app/",
        "service_description": "Authentication Microservice",
        "service_notes": (
            "Microservice responsible for User's authentication and "
            "general Pumpwood systems end-points."),
        "service_dimensions": {
            "microservice": "pumpwood-auth-app",
            "type": "core",
            "function": "authentication"},
        "service_icon": None,
        "service_extra_info": {},
        "routes": [{
            "route_url": "/service/pumpwood-auth-app/",
            "route_name": "service--aux",
            "route_type": "aux",
            "description": "Service auxiliar",
            "notes": (
                "End-point for auxliary service function such as cache "
                "invalidation, health-check, etc..."),
            "dimensions": {
                "microservice": "pumpwood-auth-app",
                "service_type": "core",
                "function": "system",
                "endpoint": "service",
                "route_type": "aux"},
            "icon": "",
            "extra_info": {}
        }, {
            "route_url": "/rest/registration/",
            "route_name": "api--registration",
            "route_type": "aux",
            "description": "Registration",
            "notes": (
                "End-point for login, logout and other Authentication "
                "functions"),
            "dimensions": {
                "microservice": "pumpwood-auth-app",
                "service_type": "core",
                "function": "authentication",
                "endpoint": "registration",
                "route_type": "aux"},
            "icon": "",
            "extra_info": {}
        }, {
            "route_url": "/rest/pumpwood/",
            "route_name": "api--pumpwood",
            "route_type": "aux",
            "description": "Pumpwood System",
            "notes": (
                "System related end-points to list Kong routes, and "
                "dummy-calls"),
            "dimensions": {
                "microservice": "pumpwood-auth-app",
                "service_type": "core",
                "function": "system",
                "endpoint": "pumpwood",
                "route_type": "aux"},
            "icon": "",
            "extra_info": {}
        }, {  # Admin
            "route_url": "/admin/pumpwood-auth-app/gui/",
            "route_name": "admin--pumpwood-auth-app",
            "route_type": "admin",
            "description": "Pumpwood Auth Admin",
            "notes": (
                "Admin for pumpwood-auth-app microservice."),
            "dimensions": {
                "microservice": "pumpwood-auth-app",
                "service_type": "core",
                "function": "gui",
                "route_type": "admin"},
            "icon": "",
            "extra_info": {}
        }, {
            "route_url": "/" + MEDIA_URL,
            "route_name": "media--pumpwood-auth-app",
            "route_type": "media",
            "description": "Pumpwood Auth Media Files",
            "notes": (
                "Path to serve files using links."),
            "dimensions": {
                "microservice": "pumpwood-auth-app",
                "service_type": "core",
                "function": "media"},
            "icon": "",
            "extra_info": {}
        }],
        "viewsets": [
            RestKongRoute,
            RestKongService,
            RestUser,
            RestUserProfile,
            RestMetabaseDashboard,
            RestMetabaseDashboardParameter,
            RestPumpwoodI8nTranslation,
            RestPumpwoodPermissionPolicy,
            RestPumpwoodPermissionPolicyAction,
            RestPumpwoodPermissionPolicyGroupM2M,
            RestPumpwoodPermissionPolicyUserM2M,
            RestPumpwoodRowPermission,
            RestPumpwoodRowPermissionGroupM2M,
            RestPumpwoodRowPermissionUserM2M,
            RestFixturesRowLevelPermission,
            RestPumpwoodUserGroup,
            RestPumpwoodUserGroupM2M]
    }

    static_service_definition = {
        "service_url": _auth_static_service,
        "service_name": "static-files",
        "healthcheck_route": None,
        "service_description": "Static Files",
        "service_notes": (
            "Static files"),
        "service_dimensions": {
            "microservice": "pumpwood",
            "type": "static"},
        "service_icon": None,
        "service_extra_info": {},
        "routes": [{
            # Admin static files
            "route_url": "/static/",
            "route_name": "static",
            "route_type": "static",
            "description": "Static Files Routes",
            "notes": (
                "Static files for all pumpwood"),
            "dimensions": {
                "microservice": "pumpwood",
                "service_type": "core",
                "route_type": "static"},
            "icon": "",
            "extra_info": {}
        }]
    }
    return {
        "auth_service": auth_service_definition,
        "static_service": static_service_definition,
    }
