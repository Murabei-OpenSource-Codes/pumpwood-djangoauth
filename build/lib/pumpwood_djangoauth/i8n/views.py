"""Create views for metabase end-points."""
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.config import storage_object, microservice
from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation
from pumpwood_djangoauth.i8n.serializers import (
    PumpwoodI8nTranslationSerializer)


class RestPumpwoodI8nTranslation(PumpWoodRestService):
    endpoint_description = "I8n Translations"
    notes = "Model to perform I8n on Pumpwood"

    service_model = PumpwoodI8nTranslation
    serializer = PumpwoodI8nTranslationSerializer
    storage_object = storage_object
    microservice = microservice
    foreign_keys = {}
    file_fields = {}

    #######
    # Gui #
    list_fields = [
        "pk", "model_class", "status", "alias", "description",
        "updated_by", "updated_at"]
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                "sentence", "tag", "plural", "language", "user_type",
                "translation"]
        }
    ]
    gui_readonly = ["updated_by", "updated_at", "extra_info"]
    gui_verbose_field = '{pk} | {description}'
    #######
