"""Django admin."""
from django.contrib import admin, messages
from pumpwood_djangoviews.views.aux import AuxViewActionReturnFile

# Register your models here.
from pumpwood_djangoauth.system.models import KongService, KongRoute


class KongServiceAdmin(admin.ModelAdmin):
    """Service admin."""
    list_display = (
        "id", "order", "service_name", "service_url", "description",
        "healthcheck_route")
    search_fields = ('description', 'service_url', 'service_name', )
    actions = ['load_kong_service', 'reload_kong_service', 'generate_doc_file']

    @admin.action(description="Load services at kong")
    def load_kong_service(self, request, queryset):
        """Load service at kong."""
        queryset_ids = [x.id for x in queryset.all()]
        if len(queryset_ids) == 0:
            KongService.load_kong_service(list_service_id=None)
            msg = "All services were loaded at kong."
            self.message_user(request, msg)
        else:
            KongService.load_kong_service(list_service_id=queryset_ids)
            msg = "{} services were loaded at kong.".format(len(queryset_ids))
            self.message_user(request, msg)

    @admin.action(description="Reload (remove/load) services at kong")
    def reload_kong_service(self, request, queryset):
        """Load service at kong."""
        queryset_ids = [x.id for x in queryset.all()]
        if len(queryset_ids) == 0:
            KongService.reload_kong_service(list_service_id=None)
            msg = "All services were reloaded at kong."
            self.message_user(request, msg)
        else:
            KongService.reload_kong_service(list_service_id=queryset_ids)
            msg = "{} services were reloaded at kong."\
                .format(len(queryset_ids))
            self.message_user(request, msg)

    @admin.action(description="Generate API documentation")
    def generate_doc_file(self, request, queryset):
        """Load service at kong."""
        queryset_ids = [x.id for x in queryset.all()]
        if len(queryset_ids) == 0:
            file_content = KongService.generate_doc_file(
                service_id_list=None)
            msg = "Documentation generated for all services."
            self.message_user(request, msg)
        else:
            file_content = KongService.generate_doc_file(
                service_id_list=queryset_ids)
            msg = "Documentation generated for {} services."\
                .format(len(queryset_ids))
            self.message_user(request, msg)
        return AuxViewActionReturnFile.run(
            action_result=file_content, mode='file')


class KongRouteAdmin(admin.ModelAdmin):
    """Route admin."""

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
        """Switch to make the routes avaiable at frontend."""
        queryset.update(availability="front_avaiable")
        msg = "Modified to avaiable: {}".format(queryset.count())
        messages.add_message(request, messages.INFO, msg)

    @admin.action(description="Make hidden")
    def make_front_hidden(self, request, queryset):
        """Switch to make the routes hidden at frontend."""
        queryset.update(availability="front_hidden")
        msg = "Modified to hidden: {}".format(queryset.count())
        messages.add_message(request, messages.INFO, msg)


##############
# User Admin #
admin.site.register(KongService, KongServiceAdmin)
admin.site.register(KongRoute, KongRouteAdmin)
