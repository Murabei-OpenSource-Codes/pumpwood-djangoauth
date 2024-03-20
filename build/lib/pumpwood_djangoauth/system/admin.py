"""Django admin."""
from django.contrib import admin
from django.contrib import messages

# Register your models here.
from pumpwood_djangoauth.system.models import KongService, KongRoute


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
    list_filter = ('service', 'availability', 'route_type', )

    actions = [
        "make_front_avaiable", "make_front_hidden", ]

    # Actions
    @admin.action(description="Make avaiable")
    def make_front_avaiable(self, request, queryset):
        queryset.update(availability="front_avaiable")
        msg = "Modified to avaiable: {}".format(queryset.count())
        messages.add_message(request, messages.INFO, msg)

    @admin.action(description="Make hidden")
    def make_front_hidden(self, request, queryset):
        queryset.update(availability="front_hidden")
        msg = "Modified to hidden: {}".format(queryset.count())
        messages.add_message(request, messages.INFO, msg)


##############
# User Admin #
admin.site.register(KongService, KongServiceAdmin)
admin.site.register(KongRoute, KongRouteAdmin)
