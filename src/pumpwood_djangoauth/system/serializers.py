"""Serializers for Kong service mesh models."""
from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, DynamicFieldsModelSerializer,
    LocalForeignKeyField, LocalRelatedField)
from pumpwood_djangoauth.system.models import KongService, KongRoute
from pumpwood_i8n.singletons import pumpwood_i8n


class KongRouteSerializer(DynamicFieldsModelSerializer):
    """Serialize ``KongRoute`` records with translated metadata fields."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    description__verbose = serializers.SerializerMethodField()
    notes__verbose = serializers.SerializerMethodField()

    # ForeignKey
    service_id = serializers.IntegerField(allow_null=False, required=True)
    service = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.system.serializers."
            "KongServiceSerializer"),
        display_field='service_name')

    class Meta:
        """Meta."""
        model = KongRoute
        fields = (
            "pk", "model_class", "availability", "service_id", "service",
            "route_url", "order", "route_name", "route_kong_id", "route_type",
            "description", "notes", "dimensions", "icon", "extra_info",
            "description__verbose", "notes__verbose")
        list_fields = [
            "pk", "order", "availability", "service_id", "route_name",
            "route_url", "route_type", "description"]

    def get_description__verbose(self, obj):
        """Return translated route description.

        Args:
            obj (KongRoute):
                Route instance being serialized.

        Returns:
            str:
                Translated description text.
        """
        return pumpwood_i8n.t(
            sentence=obj.description,
            tag="KongRoute__field__description")

    def get_notes__verbose(self, obj):
        """Return translated route notes.

        Args:
            obj (KongRoute):
                Route instance being serialized.

        Returns:
            str:
                Translated notes text.
        """
        return pumpwood_i8n.t(
            sentence=obj.notes,
            tag="KongRoute__field__notes")


class KongServiceSerializer(DynamicFieldsModelSerializer):
    """Serialize ``KongService`` records with nested routes."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    description__verbose = serializers.SerializerMethodField()
    notes__verbose = serializers.SerializerMethodField()

    # Foreign Keys
    route_set = LocalRelatedField(
        serializer=KongRouteSerializer, order_by=["-id"])

    class Meta:
        """Meta."""
        model = KongService
        fields = (
            "pk", "model_class", "service_url", "service_name",
            "order", "service_kong_id", "description", "notes",
            "healthcheck_route", "dimensions", "icon", "route_set",
            "extra_info", "description__verbose", "notes__verbose")
        list_fields = [
            "pk", "model_class", "order", "service_name", "description"]

    def get_description__verbose(self, obj):
        """Return translated service description.

        Args:
            obj (KongService):
                Service instance being serialized.

        Returns:
            str:
                Translated description text.
        """
        return pumpwood_i8n.t(
            sentence=obj.description,
            tag="KongService__field__description")

    def get_notes__verbose(self, obj):
        """Return translated service notes.

        Args:
            obj (KongService):
                Service instance being serialized.

        Returns:
            str:
                Translated notes text.
        """
        return pumpwood_i8n.t(
            sentence=obj.notes,
            tag="KongService__field__notes")
