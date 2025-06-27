"""Views for permission at end-points."""
from rest_framework.response import Response
from rest_framework.decorators import api_view
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.config import storage_object, microservice

# Models
from pumpwood_djangoauth.api_permission.models import (
    PumpwoodPermissionPolicy, PumpwoodPermissionPolicyAction,
    PumpwoodPermissionPolicyGroupM2M, PumpwoodPermissionPolicyUserM2M)

# Serializers
from pumpwood_djangoauth.api_permission.serializers import (
    SerializerPumpwoodPermissionPolicy,
    SerializerPumpwoodPermissionPolicyAction,
    SerializerPumpwoodPermissionPolicyGroupM2M,
    SerializerPumpwoodPermissionPolicyUserM2M)


@api_view(['GET'])
def view__has_permission(request):
    """Get kong routes."""
    return Response(True)


class RestPumpwoodPermissionPolicy(PumpWoodRestService):
    """End-point with Api Policies definition."""

    endpoint_description = "PumpwoodPermissionPolicy"
    notes = "Define access policy to Pumpwood End-Points"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "permission",
    }
    icon = None

    service_model = PumpwoodPermissionPolicy
    serializer = SerializerPumpwoodPermissionPolicy
    storage_object = storage_object
    microservice = microservice

    #######
    # GUI #
    gui_retrieve_fieldset = [{
        "name": "main",
        "fields": [
            'description', 'notes', 'dimensions',
            'route_id', 'can_retrieve', 'can_retrieve_file', 'can_delete',
            'can_delete_many', 'can_delete_file', 'can_save',
            'can_run_actions', "updated_by_id", "updated_at"]
        }, {
        "name": "extra-info",
        "fields": [
            'extra_info']
        },
    ]
    gui_readonly = ['extra_info', ]
    gui_verbose_field = '{pk} | {description}'
    #######


class RestPumpwoodPermissionPolicyAction(PumpWoodRestService):
    """Define custom action policies associated with a policy."""

    endpoint_description = "PumpwoodPermissionPolicyAction"
    notes = "Custom action policy"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "permission",
    }
    icon = None

    service_model = PumpwoodPermissionPolicyAction
    serializer = SerializerPumpwoodPermissionPolicyAction
    storage_object = storage_object
    microservice = microservice

    #######
    # GUI #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'pk', 'model_class', 'policy_id', 'action', 'is_allowed',
                'extra_info', "updated_by_id", "updated_at", ]
        }, {
            "name": "extra-info",
            "fields": ['extra_info']
        },
    ]
    gui_readonly = []
    gui_verbose_field = '{pk} | {policy_id} {action}'
    #######


class RestPumpwoodPermissionPolicyGroupM2M(PumpWoodRestService):
    """End-point with information about Pumpwood users."""

    endpoint_description = "PumpwoodPermissionPolicyGroupM2M"
    notes = "End-point with user information"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "permission",
    }
    icon = None

    service_model = PumpwoodPermissionPolicyGroupM2M
    serializer = SerializerPumpwoodPermissionPolicyGroupM2M
    storage_object = storage_object
    microservice = microservice
    foreign_keys = {
        "group_id": {
            "model_class": "PumpwoodPermissionGroup", "many": False},
        "custom_policy_id": {
            "model_class": "PumpwoodPermissionPolicy", "many": False},
        "updated_by_id": {
            "model_class": "User", "many": False},
    }

    #######
    # GUI #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'pk', 'model_class', 'group_id', 'general_policy',
                'custom_policy_id', 'extra_info', "updated_by_id",
                "updated_at"]
        }, {
            "name": "extra-info",
            "fields": ['extra_info']
        },
    ]
    gui_readonly = ['extra_info']
    gui_verbose_field = '{pk}}'
    #######


class RestPumpwoodPermissionPolicyUserM2M(PumpWoodRestService):
    """End-point with information about Pumpwood users."""

    endpoint_description = "PumpwoodPermissionPolicyUserM2M"
    notes = "End-point with user information"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "permission",
    }
    icon = None

    service_model = PumpwoodPermissionPolicyUserM2M
    serializer = SerializerPumpwoodPermissionPolicyUserM2M
    storage_object = storage_object
    microservice = microservice

    #######
    # GUI #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'user_id', 'general_policy',
                'custom_policy_id', 'extra_info', "updated_by_id",
                "updated_at"]
        }, {
            "name": "extra-info",
            "fields": ['extra_info']
        },
    ]
    gui_readonly = ['extra_info']
    gui_verbose_field = '{pk}}'
    #######
