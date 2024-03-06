from django.contrib import admin

# Register your models here.
from .models import KongService, KongRoute


class KongServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "order", "service_name", "service_url", "description",
        "healthcheck_route")
    search_fields = ('description', 'service_url', 'service_name', )
    # list_filter = ('description', 'route_url', 'route_name', )


class KongRouteAdmin(admin.ModelAdmin):
    list_display = (
        "id", "service", "order", "availability", "route_name", "route_url",
        "route_type", "description")
    search_fields = ('description', 'route_url', 'route_name', )
    list_filter = ('service', 'availability', )


##############
# User Admin #
admin.site.register(KongService, KongServiceAdmin)
admin.site.register(KongRoute, KongRouteAdmin)
