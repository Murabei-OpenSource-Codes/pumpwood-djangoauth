from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, CustomChoiceTypeField, CustomNestedSerializer,
    DynamicFieldsModelSerializer)
from django.contrib.auth.models import User
from .models import UserProfile


class SerializerUserProfile(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()

    class Meta:
        model = UserProfile
        fields = (
            'pk', 'model_class', 'is_microservice', 'dimentions',
            'extra_fields')


class SerializerUser(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True)
    model_class = ClassNameField()
    user_profile = SerializerUserProfile(many=False, read_only=True)
    all_permissions = serializers.SerializerMethodField()
    group_permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'pk', 'model_class', 'username', 'email', 'first_name',
            'last_name', 'last_login', 'date_joined', 'is_active', 'is_staff',
            'is_superuser', 'all_permissions', 'group_permissions',
            'user_profile')
        read_only = (
            'last_login', 'date_joined')

    def get_all_permissions(self, obj):
        all_permissions = list(obj.get_all_permissions())
        all_permissions.sort()
        return all_permissions

    def get_user_permissions(self, obj):
        user_permissions = list(obj.get_user_permissions())
        user_permissions.sort()
        return user_permissions

    def get_group_permissions(self, obj):
        group_permissions = list(obj.get_group_permissions())
        group_permissions.sort()
        return group_permissions
