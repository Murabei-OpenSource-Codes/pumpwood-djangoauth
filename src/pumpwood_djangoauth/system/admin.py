from django.contrib import admin

# Register your models here.
from .models import KongService, KongRoute


class KongServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "service_name", "service_url", "description",
        "healthcheck_route")


class KongRouteAdmin(UserAdmin):
    list_display = (
        "id", "service", "route_name", "route_url", "route_type",
        "description")


##############
# User Admin #
admin.site.register(KongService, KongServiceAdmin)
admin.site.register(KongRoute, KongRouteAdmin)
