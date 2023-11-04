# !/usr/bin/python3
# -*- coding: utf-8 -*-
# import pika
# import simplejson as json
# import logging
# from django.conf import settings
from rest_framework import serializers
from pumpwood_djangoviews.serializers import (
    ClassNameField, CustomChoiceTypeField, CustomNestedSerializer,
    DynamicFieldsModelSerializer)
from pumpwood_djangoauth.system.models import KongService, KongRoute


########
# List #
########
class KongRouteSerializer(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    service_id = serializers.IntegerField(allow_null=False, required=True)

    class Meta:
        model = KongRoute
        fields = (
            "pk", "model_class", "service_id", "route_url", "route_name",
            "route_kong_id", "route_type", "description", "notes",
            "dimensions", "icon", "extra_info")


class KongServiceSerializer(DynamicFieldsModelSerializer):
    pk = serializers.IntegerField(source='id', allow_null=True, required=False)
    model_class = ClassNameField()
    route_set = serializers.SerializerMethodField()

    class Meta:
        model = KongService
        fields = (
            "pk", "model_class", "service_url", "service_name",
            "service_kong_id", "description", "notes", "healthcheck_route",
            "dimensions", "icon", "route_set", "extra_info")

    def get_route_set(self, instance):
        songs = instance.route_set.all().order_by('description')
        return KongRouteSerializer(songs, many=True).data
