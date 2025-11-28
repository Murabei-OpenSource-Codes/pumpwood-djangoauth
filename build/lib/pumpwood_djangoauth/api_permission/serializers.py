from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, DynamicFieldsModelSerializer,
    LocalRelatedField, LocalForeignKeyField)
from pumpwood_djangoauth.api_permission.models import (
    PumpwoodPermissionPolicy, PumpwoodPermissionPolicyAction,
    PumpwoodPermissionPolicyGroupM2M, PumpwoodPermissionPolicyUserM2M)


class SerializerPumpwoodPermissionPolicy(DynamicFieldsModelSerializer):
    """Serializer for PumpwoodPermissionPolicy model."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    route_id = serializers.IntegerField(allow_null=False, required=True)

    # Foreign Key
    route = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.system.serializers.KongRouteSerializer"),
            display_field="route_name")
    updated_by = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers.SerializerUser"),
        display_field="username")

    # Related fields
    action_set = LocalRelatedField(
        serializer=(
            'pumpwood_djangoauth.api_permission.serializers.' +
            'SerializerPumpwoodPermissionPolicyAction'))

    class Meta:
        """Meta."""
        model = PumpwoodPermissionPolicy
        fields = [
            'pk', 'model_class', 'description', 'notes', 'dimensions',
            'route_id', 'route', 'can_retrieve', 'can_retrieve_file',
            'can_delete', 'can_delete_many', 'can_delete_file', 'can_save',
            'can_run_actions', 'extra_info', 'updated_by_id',
            'updated_by', 'updated_at', 'action_set']
        list_fields = [
            'pk', 'model_class', 'description', 'notes', 'dimensions',
            'route_id', 'route', 'can_retrieve', 'can_retrieve_file',
            'can_delete', 'can_delete_many', 'can_delete_file', 'can_save',
            'can_run_actions', 'extra_info', 'updated_by_id',
            'updated_by', 'updated_at']
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().update(instance, validated_data)


class SerializerPumpwoodPermissionPolicyAction(DynamicFieldsModelSerializer):
    """Serializer for PumpwoodPermissionPolicyAction model."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    policy_id = serializers.IntegerField(allow_null=False, required=True)

    # ForeignKey
    policy = LocalForeignKeyField(
        serializer=SerializerPumpwoodPermissionPolicy,
        display_field="description")
    updated_by = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers.SerializerUser"),
        display_field="username")

    class Meta:
        """Meta."""
        model = PumpwoodPermissionPolicyAction
        fields = (
            'pk', 'model_class', 'policy_id', 'action', 'is_allowed',
            'extra_info', "updated_by_id", "updated_at",
            "policy", "updated_by")
        list_fields = [
            'pk', 'model_class', 'policy_id', 'action', 'is_allowed',
            'extra_info', "updated_by_id", "updated_at",
            "policy", "updated_by"]
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().update(instance, validated_data)


class SerializerPumpwoodPermissionPolicyGroupM2M(DynamicFieldsModelSerializer):
    """Serializer for PumpwoodPermissionPolicyGroupM2M model."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # ForeignKey
    group_id = serializers.IntegerField(allow_null=False, required=True)
    group = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.groups." +
            "serializers.SerializerPumpwoodUserGroup"),
        display_field="description")
    custom_policy_id = serializers.IntegerField(
        allow_null=False, required=True)
    custom_policy = LocalForeignKeyField(
        serializer=SerializerPumpwoodPermissionPolicy,
        display_field="description")

    updated_by = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers.SerializerUser"),
        display_field="username")

    class Meta:
        """Meta."""
        model = PumpwoodPermissionPolicyGroupM2M
        fields = (
            'pk', 'model_class', 'group', 'group_id',
            'general_policy', 'custom_policy_id', "custom_policy",
            'extra_info', "updated_by_id", "updated_by", "updated_at")
        list_fields = [
            'pk', 'model_class', 'group', 'group_id',
            'general_policy', 'custom_policy_id', "custom_policy",
            'extra_info', "updated_by_id", "updated_by", "updated_at"]
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().update(instance, validated_data)


class SerializerPumpwoodPermissionPolicyUserM2M(DynamicFieldsModelSerializer):
    """Serializer for PumpwoodPermissionPolicyUserM2M model."""
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()

    # ForeignKey
    user_id = serializers.IntegerField(
        allow_null=False, required=True)
    user = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers.SerializerUser"),
        display_field="username")

    custom_policy_id = serializers.IntegerField(
        allow_null=False, required=True)
    custom_policy = LocalForeignKeyField(
        serializer=SerializerPumpwoodPermissionPolicy,
        display_field="description")

    updated_by_id = serializers.IntegerField(
        allow_null=True, required=False)
    updated_by = LocalForeignKeyField(
        serializer=(
            "pumpwood_djangoauth.registration.serializers.SerializerUser"),
        display_field="username")

    class Meta:
        """Meta."""
        model = PumpwoodPermissionPolicyUserM2M
        fields = [
            'pk', 'model_class', 'user_id', 'user',
            'general_policy', 'custom_policy_id', 'custom_policy',
            'extra_info', "updated_by_id", "updated_by", "updated_at"]
        list_fields = (
            'pk', 'model_class', 'user_id', 'user',
            'general_policy', 'custom_policy_id', 'custom_policy',
            'extra_info', "updated_by_id", "updated_by", "updated_at")
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Set updated_by_id using logged user."""
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().update(instance, validated_data)
