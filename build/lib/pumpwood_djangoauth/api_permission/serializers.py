from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, CustomChoiceTypeField, CustomNestedSerializer,
    DynamicFieldsModelSerializer)
from django.contrib.auth.models import User
from pumpwood_djangoauth.api_permission.models import (
    PumpwoodPermissionPolicy, PumpwoodPermissionPolicyAction,
    PumpwoodPermissionGroup, PumpwoodPermissionPolicyGroupM2M,
    PumpwoodPermissionPolicyUserM2M, PumpwoodPermissionUserGroupM2M)


class SerializerPumpwoodPermissionPolicy(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()
    route_id = serializers.IntegerField(allow_null=False, required=True)
    route_id = serializers.IntegerField(allow_null=False, required=True)

    class Meta:
        model = PumpwoodPermissionPolicy
        fields = (
            'pk', 'model_class', 'description', 'notes', 'dimensions',
            'route_id', 'list', 'list_without_pag', 'retrieve',
            'retrieve_file', 'delete', 'delete_many', 'delete_file', 'save',
            'extra_info', 'updated_by_id', 'updated_at')
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)


class SerializerPumpwoodPermissionPolicyAction(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()
    policy_id = serializers.IntegerField(allow_null=False, required=True)

    class Meta:
        model = PumpwoodPermissionPolicyAction
        fields = (
            'pk', 'model_class', 'policy_id', 'action', 'permission',
            'extra_info', "updated_by_id", "updated_at")
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)


class SerializerPumpwoodPermissionGroup(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()

    class Meta:
        model = PumpwoodPermissionGroup
        fields = (
            'pk', 'model_class', 'description', 'notes', 'dimensions',
            'extra_info', "updated_by_id", "updated_at")
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)


class SerializerPumpwoodPermissionUserGroupM2M(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()
    user_id = serializers.IntegerField(
        allow_null=False, required=True)
    group_id = serializers.IntegerField(
        allow_null=False, required=True)

    class Meta:
        model = PumpwoodPermissionUserGroupM2M
        fields = (
            'pk', 'model_class', 'user_id', 'group_id',
            'extra_info', 'updated_by_id', 'updated_at')
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)


class SerializerPumpwoodPermissionPolicyGroupM2M(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()
    group_id = serializers.IntegerField(
        allow_null=False, required=True)
    custom_policy_id = serializers.IntegerField(
        allow_null=False, required=True)

    class Meta:
        model = PumpwoodPermissionPolicyGroupM2M
        fields = (
            'pk', 'model_class', 'group_id', 'general_policy',
            'custom_policy_id', 'extra_info', "updated_by_id", "updated_at")
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)


class SerializerPumpwoodPermissionPolicyUserM2M(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()
    user_id = serializers.IntegerField(
        allow_null=False, required=True)
    custom_policy_id = serializers.IntegerField(
        allow_null=False, required=True)

    class Meta:
        model = PumpwoodPermissionPolicyUserM2M
        fields = (
            'pk', 'model_class', 'user_id', 'general_policy',
            'custom_policy_id', 'extra_info', "updated_by_id", "updated_at")
        read_only = ["updated_by_id", "updated_at"]

    def create(self, validated_data):
        validated_data["updated_by_id"] = self.context['request'].user.id
        return super().create(validated_data)
