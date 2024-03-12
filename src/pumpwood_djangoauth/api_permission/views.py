"""Views for authentication and user end-point."""
from django.utils import timezone
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from pumpwood_communication import exceptions
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.api_permission.models import (
    PumpwoodPermissionPolicy, PumpwoodPermissionPolicyAction,
    PumpwoodPermissionGroup, PumpwoodPermissionPolicyGroupM2M,
    PumpwoodPermissionPolicyUserM2M,
    PumpwoodPermissionUserGroupM2M)
from pumpwood_djangoauth.api_permission.serializers import (
    SerializerPumpwoodPermissionPolicy,
    SerializerPumpwoodPermissionPolicyAction,
    SerializerPumpwoodPermissionGroup,
    SerializerPumpwoodPermissionPolicyGroupM2M,
    SerializerPumpwoodPermissionPolicyUserM2M,
    SerializerPumpwoodPermissionUserGroupM2M)


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
    foreign_keys = {
        "updated_by_id": {"model_class": "User", "many": False},
    }

    #######
    # GUI #
    list_fields = [
        'pk', 'model_class', 'description', 'notes']
    gui_retrieve_fieldset = [{
        "name": "main",
        "fields": [
            'description', 'notes', 'dimensions',
            'route_id', 'list', 'list_without_pag', 'retrieve',
            'retrieve_file', 'delete', 'delete_many', 'delete_file',
            'save', "updated_by_id", "updated_at"]
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
    foreign_keys = {
        'policy_id': {
            "model_class": "PumpwoodPermissionPolicy", "many": False},
        "updated_by_id": {
            "model_class": "User", "many": False},
    }

    #######
    # GUI #
    list_fields = [
        'pk', 'model_class', 'policy_id', 'action', 'permission',
        'extra_info', "updated_by_id", "updated_at"]
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'pk', 'model_class', 'policy_id', 'action', 'permission',
                'extra_info', "updated_by_id", "updated_at", ]
        }, {
            "name": "extra-info",
            "fields": ['extra_info']
        },
    ]
    gui_readonly = []
    gui_verbose_field = '{pk} | {policy_id} {action}'
    #######


class RestPumpwoodPermissionGroup(PumpWoodRestService):
    """Groups to apply Policies for many users at same time."""

    endpoint_description = "SerializerPumpwoodPermissionGroups"
    notes = "End-point with user information"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "permission",
    }
    icon = None

    service_model = PumpwoodPermissionGroup
    serializer = SerializerPumpwoodPermissionGroup
    foreign_keys = {
        "updated_by_id": {
            "model_class": "User", "many": False},
    }

    #######
    # GUI #
    list_fields = [
        'pk', 'model_class', 'description', "updated_at"]
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'pk', 'model_class', 'description', 'notes', 'dimensions',
                "updated_by_id", "updated_at"]
        }, {
            "name": "extra-info",
            "fields": ['extra_info']
        },
    ]
    gui_readonly = ['extra_info']
    gui_verbose_field = '{pk} | {description}'
    #######


class RestPumpwoodPermissionUserGroupM2M(PumpWoodRestService):
    """Include users to policy groups."""

    endpoint_description = "PumpwoodPermissionUserGroupM2M"
    notes = "End-point with user information"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "permission",
    }
    icon = None

    service_model = PumpwoodPermissionUserGroupM2M
    serializer = SerializerPumpwoodPermissionUserGroupM2M
    foreign_keys = {
        "user_id": {
            "model_class": "User", "many": False},
        "group_id": {
            "model_class": "User", "many": False},
        "updated_by_id": {
            "model_class": "User", "many": False},
    }

    #######
    # GUI #
    list_fields = [
        'pk', 'model_class', 'description', "updated_at"]
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'pk', 'model_class', 'user_id', 'group_id',
                'extra_info', 'updated_by_id', 'updated_at']
        }, {
            "name": "extra-info",
            "fields": ['extra_info']
        },
    ]
    gui_readonly = ['extra_info']
    gui_verbose_field = '{pk} | {description}'
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
    list_fields = [
        'pk', 'model_class', 'priority', 'group_id', 'general_policy',
        'custom_policy_id']
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'pk', 'model_class', 'priority', 'group_id', 'general_policy',
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
    foreign_keys = {
        "user_id": {
            "model_class": "User", "many": False},
        "custom_policy_id": {
            "model_class": "PumpwoodPermissionPolicy", "many": False},
        "updated_by_id": {
            "model_class": "User", "many": False},
    }

    #######
    # GUI #
    list_fields = [
        'pk', 'model_class', 'priority', 'user_id', 'general_policy',
        'custom_policy_id']
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'priority', 'user_id', 'general_policy',
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
