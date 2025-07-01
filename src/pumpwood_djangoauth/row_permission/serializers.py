"""Serializer for registration end-points."""
from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, DynamicFieldsModelSerializer, LocalForeignKeyField,
    LocalRelatedField)
from pumpwood_djangoauth.row_permission.models import (
    PumpwoodRowPermission, PumpwoodRowPermissionGroupM2M,
    PumpwoodRowPermissionUserM2M)


class SerializerPumpwoodRowPermission(DynamicFieldsModelSerializer):
    """Serializer for model PumpwoodRowPermission."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # ForeignKey models
    updated_by = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers.SerializerUser"),
        display_field="username")

    # Related fields
    group_set = LocalRelatedField(
        serializer=(
            'pumpwood_djangoauth.row_permission.serializers.' +
            'SerializerPumpwoodRowPermissionGroupM2M'))
    user_set = LocalRelatedField(
        serializer=(
            'pumpwood_djangoauth.row_permission.serializers.' +
            'SerializerPumpwoodRowPermissionUserM2M'))

    class Meta:
        """Meta."""
        model = PumpwoodRowPermission
        fields = (
            'pk', 'model_class', 'description', 'notes', 'dimensions',
            'extra_info', 'updated_by', 'updated_at', 'updated_by_id',
            'group_set', 'user_set')
        list_fields = (
            'pk', 'model_class', 'is_service_user', 'dimensions',
            'extra_fields')

    def create(self, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().update(instance, validated_data)


class SerializerPumpwoodRowPermissionGroupM2M(DynamicFieldsModelSerializer):
    """Serializer for model PumpwoodRowPermissionGroupM2M."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # Foreign Key models
    updated_by = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers.SerializerUser"),
        display_field="username")

    group_id = serializers.IntegerField(
        allow_null=False, required=True)
    group = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.groups." +
            "serializers.SerializerPumpwoodUserGroup"),
        display_field="description")
    row_permission_id = serializers.IntegerField(
        allow_null=False, required=True)
    row_permission = LocalForeignKeyField(
        serializer=SerializerPumpwoodRowPermission,
        display_field="description")

    class Meta:
        """Meta."""
        model = PumpwoodRowPermissionGroupM2M
        fields = (
            'pk', 'model_class', 'group_id', 'group', 'row_permission_id',
            'row_permission', 'updated_by', 'updated_by_id', 'extra_info')
        list_fields = (
            'pk', 'model_class', 'group_id', 'group', 'row_permission_id',
            'row_permission', 'updated_by', 'updated_by_id')

    def create(self, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().update(instance, validated_data)


class SerializerPumpwoodRowPermissionUserM2M(DynamicFieldsModelSerializer):
    """Serializer for model PumpwoodRowPermissionUserM2M."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # Foreign Key models
    updated_by = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers.SerializerUser"),
        display_field="username")

    user_id = serializers.IntegerField(
        allow_null=False, required=True)
    user = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers.SerializerUser"),
        display_field="username")
    row_permission_id = serializers.IntegerField(
        allow_null=False, required=True)
    row_permission = LocalForeignKeyField(
        serializer=SerializerPumpwoodRowPermission,
        display_field="description")

    class Meta:
        """Meta."""
        model = PumpwoodRowPermissionUserM2M
        fields = (
            'pk', 'model_class', 'user', 'row_permission', 'extra_info',
            'updated_by', 'updated_at', 'user_id', 'row_permission_id')
        list_fields = (
            'pk', 'model_class', 'user', 'row_permission',
            'updated_by', 'updated_at', 'user_id', 'row_permission_id')

    def create(self, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().update(instance, validated_data)
