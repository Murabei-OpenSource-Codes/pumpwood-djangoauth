# Create your views here.
"""Views for authentication and user end-point."""
from pumpwood_djangoauth.config import storage_object, microservice
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.groups.models import (
    PumpwoodUserGroup, PumpwoodUserGroupM2M)
from pumpwood_djangoauth.groups.serializers import (
    SerializerPumpwoodUserGroup, SerializerPumpwoodUserGroupM2M)


class RestPumpwoodUserGroup(PumpWoodRestService):
    """Groups users at Pumpwood."""

    endpoint_description = "Pumpwood User Group"
    notes = (
        "Groups of users at Pumpwood used to organize users and apply "
        "End-Point/Row permissions.")
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "permission",
    }
    icon = None

    service_model = PumpwoodUserGroup
    serializer = SerializerPumpwoodUserGroup
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


class RestPumpwoodUserGroupM2M(PumpWoodRestService):
    """Many to Many relations between groups and users at Pumpwood."""

    endpoint_description = "Pumpwood User Group M2M"
    notes = (
        "End-point to associate users to groups on Pumpwood")
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "permission",
    }
    icon = None

    service_model = PumpwoodUserGroupM2M
    serializer = SerializerPumpwoodUserGroupM2M
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
