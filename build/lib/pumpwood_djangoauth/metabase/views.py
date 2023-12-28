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
        "pk", "model_class", "status", "alias", "description",
        "auto_embedding", "object_model_class", "object_pk",
        "updated_by", "updated_at"]

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
