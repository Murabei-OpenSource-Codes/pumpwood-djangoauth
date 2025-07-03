"""Create admin for API permission."""
from django.contrib import admin
from pumpwood_djangoauth.groups.models import (
    PumpwoodUserGroup, PumpwoodUserGroupM2M)
from pumpwood_djangoauth.groups.forms import (
    PumpwoodUserGroupAdminForm, PumpwoodUserGroupM2MAdminForm)


class PumpwoodUserGroupM2MInline(admin.TabularInline):
    """Inline PumpwoodUserGroupM2M."""
    model = PumpwoodUserGroupM2M
    extra = 0
    fields = ['user']
    ordering = ('user__username', )


@admin.register(PumpwoodUserGroup)
class PumpwoodUserGroupAdmin(admin.ModelAdmin):
    """Admin for PumpwoodUserGroup model."""
    form = PumpwoodUserGroupAdminForm

    list_filter = []
    search_fields = ["description", "notes", ]

    list_display = (
        "description", "notes", "updated_by", "updated_at",)
    readonly_fields = ['updated_by', 'updated_at']
    inlines = [
        PumpwoodUserGroupM2MInline, ]
    fieldsets = ((
             None, {
                 'fields': (
                     'description', 'notes', 'updated_by', 'updated_at')
                 }
         ), (
             'Extra-info', {
                 'fields': ('extra_info', 'dimensions')
             }

         )
    )

    def save_model(self, request, obj, form, change):
        """Save model add updated_by field."""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """Add updated_by field to m2m models."""
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()

        for instance in instances:
            if isinstance(instance, PumpwoodUserGroupM2M):
                instance.updated_by = request.user
                instance.save()
            else:
                instance.save()
        formset.save_m2m()

    def get_route_name(self, obj=None):
        """Get route name to display on object."""
        if obj.id is None:
            return "-"
        return obj.route.route_name
    get_route_name.allow_tags = True
    get_route_name.__name__ = "Route"


@admin.register(PumpwoodUserGroupM2M)
class PumpwoodUserGroupM2MAdmin(admin.ModelAdmin):
    """Admin for PumpwoodPermissionPolicy model."""
    form = PumpwoodUserGroupM2MAdminForm
    list_display = (
        "user", "group", "updated_by", "updated_at", )
    list_filter = ["user", "group"]
    search_fields = []
    readonly_fields = ['updated_by', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Save model add updated_by field."""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
