"""Create Serializers."""
from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, DynamicFieldsModelSerializer)
from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation


class PumpwoodI8nTranslationSerializer(DynamicFieldsModelSerializer):
    """PumpwoodI8nTranslation Serializer."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    class Meta:
        """Meta."""
        model = PumpwoodI8nTranslation
        fields = (
            "pk", "model_class", "sentence", "tag", "plural",
            "language", "user_type", "translation", "do_not_remove",
            "last_used_at")
        list_fields = (
            "pk", "model_class", "sentence", "tag", "plural",
            "language", "user_type", "translation", "do_not_remove",
            "last_used_at")
        read_only = ["updated_by", "last_used_at"]
