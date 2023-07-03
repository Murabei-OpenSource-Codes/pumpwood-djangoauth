"""Create views for metabase end-points."""
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.config import storage_object, microservice, rabbitmq_api
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

    list_fields = [
        "pk", "model_class", "status", "description", "notes",
        "metabase_id", "expire_in_min", "default_theme",
        "default_is_bordered", "default_is_titled", "dimensions",
        "extra_info", "updated_by", "updated_at"]

    foreign_keys = {
        "updated_by": {"model_class": "User", "many": False},
    }

    file_fields = {
    }


class RestMetabaseDashboardParameter(PumpWoodRestService):
    endpoint_description = "Metabase Dashboard parameters"
    notes = "Metabase Dashboard parameters"

    service_model = MetabaseDashboardParameter
    serializer = MetabaseDashboardParameterSerializer
    storage_object = storage_object
    microservice = microservice

    list_fields = [
        "pk", "model_class", "dashboard_id", "name",
        "notes", "type", "default_value"]

    foreign_keys = {
        "dashboard_id": {
            "model_class": "MetabaseDashboard", "many": False},
    }

    file_fields = {
    }
