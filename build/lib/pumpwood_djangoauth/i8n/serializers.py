"""Create Serializers."""
from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, DynamicFieldsModelSerializer)
from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation


class PumpwoodI8nTranslationSerializer(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    class Meta:
        model = PumpwoodI8nTranslation
        fields = (
            "pk", "model_class", "sentence", "tag", "plural",
            "language", "user_type", "translation")
