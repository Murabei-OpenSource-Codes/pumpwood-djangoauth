"""Create views for metabase end-points."""
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.config import storage_object, microservice
from pumpwood_djangoauth.metabase.models import (
    MetabaseDashboard, MetabaseDashboardParameter)
from pumpwood_djangoauth.metabase.serializers import (
    MetabaseDashboardSerializer, MetabaseDashboardParameterSerializer)


class RestMetabaseDashboard(PumpWoodRestService):
    endpoint_description = "Metabase Dashboard"
    notes = "Register and generate url to embed Metabase dashboards"

    service_model = MetabaseDashboard
    serializer = MetabaseDashboardSerializer
    storage_object = storage_object
    microservice = microservice

    file_fields = {
    }

    #######
    # Gui #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                "status", "alias", "description", "notes", "dimensions",
                "updated_by", "updated_at"]
        }, {
            "name": "embedding",
            "fields": [
                "metabase_id", "auto_embedding", "object_model_class",
                "object_pk"]
        }, {
            "name": "config",
            "fields": [
                "expire_in_min", "default_theme",
                "default_is_bordered", "default_is_titled"]
        }, {
            "name": "extra_info",
            "fields": ["extra_info"]
        }
    ]
    gui_readonly = ["updated_by_id", "updated_at", "extra_info"]
    gui_verbose_field = '{pk} | {description}'
    #######


class RestMetabaseDashboardParameter(PumpWoodRestService):
    endpoint_description = "Metabase Dashboard parameters"
    notes = "Metabase Dashboard parameters"
    service_model = MetabaseDashboardParameter
    serializer = MetabaseDashboardParameterSerializer
    storage_object = storage_object
    microservice = microservice

    file_fields = {
    }

    #######
    # Gui #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                "dashboard_id", "name", "notes", "type", "default_value"]
        }
    ]
    gui_readonly = []
    gui_verbose_field = '{dashboard_id} | {name}'
    #######
