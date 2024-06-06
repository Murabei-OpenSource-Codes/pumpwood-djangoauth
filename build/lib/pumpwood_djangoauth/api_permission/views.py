"""Views for authentication and user end-point."""
import pandas as pd
import numpy as np
from django.utils import timezone
from django.db import connection
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from pumpwood_communication import exceptions
from pumpwood_djangoauth.config import (
    storage_object, microservice, rabbitmq_api)
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


def get_user_permissions(user_id: int, route_name: str = None):
    query_results = None
    if route_name is not None:
        query = """
            SELECT *
            FROM public.api_permission__list_all_permissions
            WHERE user_id = %(user_id)s
              AND route_name = %(route_name)s
        """
        query_results = pd.read_sql(
            query, con=connection, params={
                "user_id": user_id,
                "route_name": route_name})
    else:
        query = """
            SELECT *
            FROM public.api_permission__list_all_permissions
            WHERE user_id = %(user_id)s
        """
        query_results = pd.read_sql(
            query, con=connection, params={
                "user_id": user_id
            })

    # Custom action policy
    is_custom_action = query_results["can_run_actions"] == 'custom'
    custom_action = query_results[is_custom_action]
    unique_policy_id = custom_action["policy_id"].dropna().unique().tolist()
    action_policy = pd.DataFrame(
        PumpwoodPermissionPolicyAction.objects
        .filter(policy_id__in=unique_policy_id)
        .values('policy_id', 'action', 'permission'),
        columns=['policy_id', 'action', 'permission'])
    custom_action = custom_action[[
        "policy_id", 'user_id', 'group_id', "priority",
        "route_id", "route_name"]].merge(
        action_policy, on="policy_id", validate="1:m")
    return {
        "permission_policy": query_results.replace({np.nan: None}),
        "permission_custom_action": custom_action.replace({np.nan: None})}


@api_view(['GET'])
def view__list_self_permissions(request):
    """Get kong routes."""
    user = request.user
    route_name = request.GET.get('route_name')
    query_results = get_user_permissions(
        user_id=user.id, route_name=route_name)
    return Response(query_results)


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
    list_fields = [
        'pk', 'model_class', 'description', 'notes']
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
    storage_object = storage_object
    microservice = microservice
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
    storage_object = storage_object
    microservice = microservice
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
    storage_object = storage_object
    microservice = microservice

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
