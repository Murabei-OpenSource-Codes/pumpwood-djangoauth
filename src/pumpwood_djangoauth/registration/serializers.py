"""Serializer for registration end-points."""
from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, DynamicFieldsModelSerializer, LocalForeignKeyField,
    LocalRelatedField)
from django.contrib.auth.models import User
from pumpwood_djangoauth.registration.models import (
    UserProfile, PumpwoodMFAMethod, PumpwoodMFAToken, PumpwoodMFACode,
    PumpwoodMFARecoveryCode)


class SerializerUserProfile(DynamicFieldsModelSerializer):
    """Serializer for model UserProfile."""
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()

    class Meta:
        """Meta."""
        model = UserProfile
        fields = (
            'pk', 'model_class', 'is_service_user', 'dimensions',
            'extra_fields')
        list_fields = (
            'pk', 'model_class', 'is_service_user', 'dimensions',
            'extra_fields')


class SerializerPumpwoodMFAMethod(DynamicFieldsModelSerializer):
    """Serializer for model PumpwoodMFAMethod."""
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()

    # ForeignKey
    user_id = serializers.IntegerField(allow_null=False, required=True)
    user = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration."
            "serializers.SerializerUser"))

    class Meta:
        """Meta."""
        model = PumpwoodMFAMethod
        fields = (
            'pk', 'model_class', 'is_enabled', 'priority', 'user_id',
            'user', 'type', 'mfa_parameter', 'extra_info')
        list_fields = (
            'pk', 'model_class', 'is_enabled', 'priority', 'user_id',
            'user', 'type', 'mfa_parameter', 'extra_info')


class SerializerPumpwoodMFAToken(DynamicFieldsModelSerializer):
    """Serializer for model PumpwoodMFAToken."""
    pk = serializers.IntegerField(source='token', allow_null=True)
    model_class = ClassNameField()

    # ForeignKey
    user_id = serializers.IntegerField(allow_null=False, required=True)
    user = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration."
            "serializers.SerializerUser"))

    class Meta:
        """Meta."""
        model = PumpwoodMFAToken
        fields = (
            'pk', 'model_class', "token", "user_id", "user",
            "created_at", "expire_at")
        list_fields = (
            'pk', 'model_class', "token", "user_id", "user",
            "created_at", "expire_at")


class SerializerPumpwoodMFACode(DynamicFieldsModelSerializer):
    """Serializer for model PumpwoodMFACode."""
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()

    class Meta:
        """Meta."""
        model = PumpwoodMFACode
        fields = (
            'pk', 'model_class', 'token', 'mfa_method', 'code',
            'created_at')
        list_fields = (
            'pk', 'model_class', 'token', 'mfa_method', 'code',
            'created_at')


class SerializerPumpwoodMFARecoveryCode(DynamicFieldsModelSerializer):
    """Serializer for model PumpwoodMFARecoveryCode."""
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()

    # ForeignKey
    user_id = serializers.IntegerField(allow_null=False, required=True)
    user = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration."
            "serializers.SerializerUser"))

    class Meta:
        """Meta."""
        model = PumpwoodMFARecoveryCode
        fields = (
            'pk', 'model_class', 'user_id', 'user', 'code', 'created_at')
        list_fields = (
            'pk', 'model_class', 'user_id', 'user', 'code', 'created_at')


class SerializerUser(DynamicFieldsModelSerializer):
    """Serializer for model User."""
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()
    user_profile = SerializerUserProfile(many=False, read_only=True)
    all_permissions = serializers.SerializerMethodField()
    group_permissions = serializers.SerializerMethodField()

    # ForeignKey
    mfa_method_set = LocalRelatedField(
        serializer=SerializerPumpwoodMFAMethod,
        order_by=["-id"])
    mfa_token_set = LocalRelatedField(
        serializer=SerializerPumpwoodMFAToken,
        order_by=["-created_at"])
    recovery_codes_set = LocalRelatedField(
        serializer=SerializerPumpwoodMFARecoveryCode,
        order_by=["-id"])
    api_permission_set = LocalRelatedField(
        serializer=(
            "pumpwood_djangoauth.api_permission." +
            "serializers.SerializerPumpwoodPermissionPolicyUserM2M"),
        order_by=["-id"])
    user_group_m2m_set = LocalRelatedField(
        serializer=(
            "pumpwood_djangoauth.groups." +
            "serializers.SerializerPumpwoodUserGroupM2M"),
        order_by=["-id"])

    class Meta:
        """Meta."""
        model = User
        fields = (
            'pk', 'model_class', 'username', 'email', 'first_name',
            'last_name', 'last_login', 'date_joined', 'is_active', 'is_staff',
            'is_superuser', 'all_permissions', 'group_permissions',
            'user_profile', 'mfa_method_set', 'api_permission_set',
            'user_group_m2m_set', 'mfa_method_set', 'mfa_token_set',
            'recovery_codes_set')
        list_fields = [
            "pk", "model_class", 'is_active', 'is_superuser', 'is_staff',
            'username', 'email', 'last_login']
        read_only = ('last_login', 'date_joined')

    def get_all_permissions(self, obj):
        """Get all possible permissions."""
        all_permissions = list(obj.get_all_permissions())
        all_permissions.sort()
        return all_permissions

    def get_user_permissions(self, obj):
        """Get user's permissions."""
        user_permissions = list(obj.get_user_permissions())
        user_permissions.sort()
        return user_permissions

    def get_group_permissions(self, obj):
        """Get group permission."""
        group_permissions = list(obj.get_group_permissions())
        group_permissions.sort()
        return group_permissions
