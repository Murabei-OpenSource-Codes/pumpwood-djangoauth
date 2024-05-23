import pumpwood_djangoauth.i8n.translate as _
from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, CustomChoiceTypeField, CustomNestedSerializer,
    DynamicFieldsModelSerializer, MicroserviceForeignKeyField,
    MicroserviceRelatedField)
from pumpwood_communication.serializers import PumpWoodJSONEncoder
from pumpwood_djangoauth.system.models import KongService, KongRoute
from pumpwood_djangoauth.config import microservice


########
# List #
class KongRouteSerializer(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    description__verbose = serializers.SerializerMethodField()
    notes__verbose = serializers.SerializerMethodField()

    # ForeignKey
    service_id = serializers.IntegerField(allow_null=False, required=True)
    service = MicroserviceForeignKeyField(
        model_class="KongService", source="service_id",
        microservice=microservice, display_field='service_name')

    class Meta:
        model = KongRoute
        fields = (
            "pk", "model_class", "availability", "service_id", "service",
            "route_url", "order", "route_name", "route_kong_id", "route_type",
            "description", "notes", "dimensions", "icon", "extra_info",
            "description__verbose", "notes__verbose")

    def get_description__verbose(self, obj):
        """Translate description."""
        return str(_.t(
            sentence=obj.description,
            tag="KongRoute__field__description"))

    def get_notes__verbose(self, obj):
        """Translate notes."""
        return str(_.t(
            sentence=obj.notes,
            tag="KongRoute__field__notes"))


class KongServiceSerializer(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    route_set = serializers.SerializerMethodField()
    description__verbose = serializers.SerializerMethodField()
    notes__verbose = serializers.SerializerMethodField()

    # ForeignKey
    route_set = MicroserviceRelatedField(
        microservice=microservice,
        write_only=False, model_class='KongRoute',
        foreign_key='service_id', order_by=["route_name"])

    class Meta:
        model = KongService
        fields = (
            "pk", "model_class", "service_url", "service_name",
            "order", "service_kong_id", "description", "notes",
            "healthcheck_route", "dimensions", "icon", "route_set",
            "extra_info", "description__verbose", "notes__verbose")

    def get_description__verbose(self, obj):
        """Translate description."""
        return str(_.t(
            sentence=obj.description,
            tag="KongService__field__description"))

    def get_notes__verbose(self, obj):
        """Translate notes."""
        return str(_.t(
            sentence=obj.notes,
            tag="KongService__field__notes"))

    def get_route_set(self, instance):
        routes = instance.route_set.all().order_by('description')
        return KongRouteSerializer(routes, many=True).data
