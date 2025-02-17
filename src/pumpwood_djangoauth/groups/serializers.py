"""Serializers for user groups."""
from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, DynamicFieldsModelSerializer,
    LocalForeignKeyField)
from pumpwood_djangoauth.groups.models import (
    PumpwoodUserGroup, PumpwoodUserGroupM2M)


class SerializerPumpwoodUserGroup(DynamicFieldsModelSerializer):
    """Serializer associated with PumpwoodUserGroup object."""

    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # ForeignKey
    updated_by_id = serializers.IntegerField(allow_null=False, required=True)
    updated_by = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers."
            "SerializerUser"))

    class Meta:
        """Meta class."""
        model = PumpwoodUserGroup
        fields = (
            'pk', 'model_class', 'description', 'notes', 'dimensions',
            'extra_info', "updated_by_id", "updated_at", 'updated_by')
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        """Add user on object creation."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Add user on object update."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().update(instance, validated_data)


class SerializerPumpwoodUserGroupM2M(DynamicFieldsModelSerializer):
    """Serializer associated with PumpwoodUserGroupM2M object."""

    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # ForeignKey
    group_id = serializers.IntegerField(allow_null=False, required=True)
    group = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.groups.serializers."
            "SerializerPumpwoodUserGroup"))

    user_id = serializers.IntegerField(allow_null=False, required=True)
    user = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers."
            "SerializerUser"))

    updated_by_id = serializers.IntegerField(allow_null=False, required=True)
    updated_by = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers."
            "SerializerUser"))

    class Meta:
        """Meta class."""
        model = PumpwoodUserGroupM2M
        fields = (
            'pk', 'model_class', 'user_id', 'user', 'group_id', 'group',
            'extra_info', 'updated_by_id', 'updated_by', 'updated_at')
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        """Add user on object creation."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Add user on object update."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().update(instance, validated_data)
