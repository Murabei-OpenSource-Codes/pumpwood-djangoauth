from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, CustomChoiceTypeField, CustomNestedSerializer,
    DynamicFieldsModelSerializer, MicroserviceForeignKeyField,
    MicroserviceRelatedField)
from django.contrib.auth.models import User
from pumpwood_djangoauth.metabase.models import (
    MetabaseDashboard, MetabaseDashboardParameter)
from pumpwood_djangoauth.config import microservice


class MetabaseDashboardSerializer(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    updated_by = MicroserviceForeignKeyField(
        model_class="User", source="updated_by_id",
        microservice=microservice, required=False,
        display_field='username')
    parameter_set = MicroserviceRelatedField(
        model_class="MetabaseDashboardParameter",
        microservice=microservice, foreign_key='dashboard_id',
        help_text="Parameters associated with Dashboard")

    class Meta:
        model = MetabaseDashboard
        fields = (
            "pk", "model_class", "status", "alias", "description", "notes",
            "auto_embedding", "object_model_class", "object_pk", "metabase_id",
            "expire_in_min", "default_theme", "default_is_bordered",
            "default_is_titled", "dimensions", "extra_info",
            "updated_by", "updated_by_id", "updated_at", 'parameter_set', )
        read_only = ["updated_by_id", "updated_by", "updated_at"]

    def create(self, validated_data):
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)


class MetabaseDashboardParameterSerializer(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    dashboard_id = serializers.IntegerField(allow_null=False, required=True)
    dashboard = MicroserviceForeignKeyField(
        model_class="MetabaseDashboard", source="dashboard_id",
        microservice=microservice, required=False,
        display_field='description')

    class Meta:
        model = MetabaseDashboardParameter
        fields = (
            "pk", "model_class", "dashboard", "dashboard_id", "name",
            "notes", "type", "default_value")
