"""Create admin for API permission."""
from django.contrib import admin
from pumpwood_djangoauth.row_permission.models import (
    PumpwoodRowPermission, PumpwoodRowPermissionGroupM2M,
    PumpwoodRowPermissionUserM2M)
from pumpwood_djangoauth.row_permission.forms import (
    PumpwoodRowPermissionAdminForm)


class PumpwoodRowPermissionGroupM2MInline(admin.TabularInline):
    """Inline PumpwoodRowPermissionGroupM2M."""
    model = PumpwoodRowPermissionGroupM2M
    extra = 0
    fields = ['group', 'updated_by', 'updated_at']
    readonly_fields = ('updated_by', 'updated_at', )
    ordering = ('-updated_at', )


class PumpwoodRowPermissionUserM2MInline(admin.TabularInline):
    """Group permission m2m inline."""
    model = PumpwoodRowPermissionUserM2M
    extra = 0
    fields = ['user', 'updated_by', 'updated_at', ]
    readonly_fields = ('updated_by', 'updated_at', )
    ordering = ('-updated_at', )


@admin.register(PumpwoodRowPermission)
class PumpwoodPermissionPolicyAdmin(admin.ModelAdmin):
    """Admin for PumpwoodPermissionPolicy model."""
    form = PumpwoodRowPermissionAdminForm

    list_filter = []
    search_fields = ["description", "notes", ]

    list_display = (
        "description", "notes", "dimensions", "extra_info", "updated_by",
        "updated_at")
    readonly_fields = ["updated_by", "updated_at"]

    inlines = [
        PumpwoodRowPermissionGroupM2MInline,
        PumpwoodRowPermissionUserM2MInline]

    fieldsets = ((
             None, {
                 'fields': (
                     'description', 'notes', 'dimensions',
                     'updated_by', 'updated_at',
                 )}
         ), (
             'Extra-info', {
                 'fields': ('extra_info', ), }

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
            if isinstance(instance, PumpwoodRowPermissionGroupM2MInline):
                instance.updated_by = request.user
                instance.save()
            elif isinstance(instance, PumpwoodRowPermissionUserM2MInline):
                instance.updated_by = request.user
                instance.save()
            else:
                instance.save()
        formset.save_m2m()
