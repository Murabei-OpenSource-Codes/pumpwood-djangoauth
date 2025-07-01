"""Create views for system end-points."""
from pumpwood_djangoviews.views import PumpWoodRestService

# Models
from pumpwood_djangoauth.row_permission.models import (
    PumpwoodRowPermission, PumpwoodRowPermissionGroupM2M,
    PumpwoodRowPermissionUserM2M)

# Serializers
from pumpwood_djangoauth.row_permission.serializers import (
    SerializerPumpwoodRowPermission, SerializerPumpwoodRowPermissionGroupM2M,
    SerializerPumpwoodRowPermissionUserM2M)


class RestPumpwoodRowPermission(PumpWoodRestService):
    """Rest for model PumpwoodRowPermission."""
    endpoint_description = "Pumpwood Row Permission"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "row-permission",
        "sub_type": "dimensions",
    }
    icon = None

    service_model = PumpwoodRowPermission
    serializer = SerializerPumpwoodRowPermission

    #######
    # GUI #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'description', 'notes', 'dimensions', 'extra_info',
                'updated_by', 'updated_at', 'updated_by_id']
        }
    ]
    gui_readonly = []
    gui_verbose_field = '{pk} | {description}'


class RestPumpwoodRowPermissionGroupM2M(PumpWoodRestService):
    """Rest for model PumpwoodRowPermissionGroupM2M."""
    endpoint_description = "Pumpwood Row Permission Group M2M"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "row-permission",
        "sub_type": "group-m2m",
    }
    icon = None

    service_model = PumpwoodRowPermissionGroupM2M
    serializer = SerializerPumpwoodRowPermissionGroupM2M

    #######
    # GUI #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'pk', 'model_class', 'group_id', 'group', 'row_permission_id',
                'row_permission', 'updated_by', 'updated_by_id', 'extra_info']
        }
    ]
    gui_readonly = []
    gui_verbose_field = '{pk} | {row_permission_id} -> {group_id}'


class RestPumpwoodRowPermissionUserM2M(PumpWoodRestService):
    """Rest for model PumpwoodRowPermissionUserM2M."""
    endpoint_description = "Pumpwood Row Permission User M2M"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "row-permission",
        "sub_type": "user-m2m",
    }
    icon = None

    service_model = PumpwoodRowPermissionUserM2M
    serializer = SerializerPumpwoodRowPermissionUserM2M

    #######
    # GUI #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'user', 'row_permission', 'extra_info', 'updated_by',
                'updated_at', 'user_id', 'row_permission_id']
        }
    ]
    gui_readonly = []
    gui_verbose_field = '{pk} | {row_permission_id} -> {user_id}'
