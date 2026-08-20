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
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    self_api_permissions = serializers.SerializerMethodField()
    self_row_permissions = serializers.SerializerMethodField()

    class Meta:
        """Meta."""
        model = UserProfile
        fields = (
            'pk', 'model_class', 'is_service_user', 'dimensions',
            'extra_fields', 'self_api_permissions', 'self_row_permissions')
        list_fields = (
            'pk', 'model_class', 'is_service_user', 'dimensions',
            'extra_fields', 'self_api_permissions', 'self_row_permissions')

    def _serialize_permission_result(self, result):
        """Convert UserProfile permission results to JSON-safe data.

        Args:
            result (list | DataFrame):
                Permission payload from ``UserProfile`` actions.

        Returns:
            list:
                JSON-serializable permission records.
        """
        if hasattr(result, 'to_dict'):
            return result.to_dict(orient='records')
        return result

    def get_self_api_permissions(self, obj):
        """Return effective API permissions for the profile user.

        Args:
            obj (UserProfile):
                Profile instance being serialized.

        Returns:
            list:
                Effective API permissions from
                ``UserProfile.user_api_permissions``. Empty when request
                context is missing.
        """
        request = self.context.get('request')
        if request is None:
            return []
        result = UserProfile.user_api_permissions(
            user_id=obj.user_id, request=request)
        return self._serialize_permission_result(result)

    def get_self_row_permissions(self, obj):
        """Return effective row permissions for the profile user.

        Args:
            obj (UserProfile):
                Profile instance being serialized.

        Returns:
            list:
                Effective row permissions from
                ``UserProfile.user_row_permissions``. Empty when request
                context is missing.
        """
        request = self.context.get('request')
        if request is None:
            return []
        return UserProfile.user_row_permissions(
            user_id=obj.user_id, request=request)


class SerializerPumpwoodMFAMethod(DynamicFieldsModelSerializer):
    """Serializer for model PumpwoodMFAMethod."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # ForeignKey
    user_id = serializers.IntegerField(allow_null=False, required=True)
    user = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration."
            "serializers.SerializerUser"),
        display_field="full_name")

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
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # ForeignKey
    user_id = serializers.IntegerField(allow_null=False, required=True)
    user = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration."
            "serializers.SerializerUser"),
        display_field="full_name")

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
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
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
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # ForeignKey
    user_id = serializers.IntegerField(allow_null=False, required=True)
    user = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration."
            "serializers.SerializerUser"),
        display_field="full_name")

    class Meta:
        """Meta."""
        model = PumpwoodMFARecoveryCode
        fields = (
            'pk', 'model_class', 'user_id', 'user', 'code', 'created_at')
        list_fields = (
            'pk', 'model_class', 'user_id', 'user', 'code', 'created_at')


class SerializerUser(DynamicFieldsModelSerializer):
    """Serializer for model User."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    user_profile = SerializerUserProfile(many=False, read_only=True)
    all_permissions = serializers.SerializerMethodField()
    group_permissions = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

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
    row_permission_set = LocalRelatedField(
        serializer=(
            "pumpwood_djangoauth.row_permission." +
            "serializers.SerializerPumpwoodRowPermissionUserM2M"),
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
            'recovery_codes_set', 'row_permission_set', 'full_name')
        list_fields = [
            "pk", "model_class", 'is_active', 'is_superuser', 'is_staff',
            'username', 'email', 'last_login', 'full_name',
            'first_name', 'last_name']
        read_only = ('last_login', 'date_joined', 'full_name')

    def get_all_permissions(self, obj):
        """Get all possible permissions."""
        all_permissions = list(obj.get_all_permissions())
        all_permissions.sort()
        return all_permissions

    def get_group_permissions(self, obj):
        """Get group permission."""
        group_permissions = list(obj.get_group_permissions())
        group_permissions.sort()
        return group_permissions

    def get_full_name(self, obj):
        """Return user's full name."""
        return "{first_name} {last_name}"\
            .format(first_name=obj.first_name, last_name=obj.last_name)\
            .strip()
