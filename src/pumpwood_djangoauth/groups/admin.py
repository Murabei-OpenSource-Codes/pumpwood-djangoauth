"""Create admin for API permission."""
from django.contrib import admin
from pumpwood_djangoauth.groups.models import (
    PumpwoodUserGroup, PumpwoodUserGroupM2M)
from pumpwood_djangoauth.groups.forms import (
    PumpwoodUserGroupAdminForm, PumpwoodUserGroupM2MAdminForm)
from pumpwood_djangoauth.api_permission.models import (
    PumpwoodPermissionPolicyGroupM2M)
from pumpwood_djangoauth.row_permission.models import (
    PumpwoodRowPermissionGroupM2M)


class PumpwoodPermissionPolicyGroupM2MInline(admin.TabularInline):
    """Inline PumpwoodPermissionPolicyGroupM2M."""
    model = PumpwoodPermissionPolicyGroupM2M
    extra = 0
    fields = [
        'group', 'general_policy', 'custom_policy',
        'get_route_name', 'get_can_list', 'get_can_list_without_pag',
        'get_can_retrieve', 'get_can_retrieve_file', 'get_can_delete',
        'get_can_delete_many', 'get_can_delete_file', 'get_can_save',
        'get_can_run_actions', ]
    readonly_fields = (
        'get_route_name', 'get_can_list', 'get_can_list_without_pag',
        'get_can_retrieve', 'get_can_retrieve_file', 'get_can_delete',
        'get_can_delete_many', 'get_can_delete_file', 'get_can_save',
        'get_can_run_actions', )
    ordering = ('general_policy', 'custom_policy__description')

    def get_route_name(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.custom_policy.route.route_name
        return None
    get_route_name.__name__ = "Route"

    def get_can_list(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.can_list
        return None
    get_can_list.__name__ = "List?"

    def get_can_list_without_pag(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.can_list_without_pag
        return None
    get_can_list_without_pag.__name__ = "List no pag.?"

    def get_can_retrieve(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.can_retrieve
        return None
    get_can_retrieve.__name__ = "Retrieve?"

    def get_can_retrieve_file(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.can_retrieve_file
        return None
    get_can_retrieve_file.__name__ = "Retrieve file?"

    def get_can_delete(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.can_delete
        return None
    get_can_delete.__name__ = "Delete?"

    def get_can_delete_many(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.can_delete_many
        return None
    get_can_delete_many.__name__ = "Delete many?"

    def get_can_delete_file(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.can_delete_file
        return None
    get_can_delete_file.__name__ = "Delete file?"

    def get_can_save(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.can_save
        return None
    get_can_save.__name__ = "Save?"

    def get_can_run_actions(self, obj=None):
        """Get route name to display on object."""
        if obj is not None:
            if obj.custom_policy is not None:
                return obj.can_run_actions
        return None
    get_can_run_actions.__name__ = "Run actions?"


class PumpwoodRowPermissionGroupM2MInline(admin.TabularInline):
    """Inline PumpwoodRowPermissionGroupM2M."""
    model = PumpwoodRowPermissionGroupM2M
    extra = 0
    fields = ['row_permission']
    ordering = ('row_permission__description', )


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
        PumpwoodUserGroupM2MInline,
        PumpwoodPermissionPolicyGroupM2MInline,
        PumpwoodRowPermissionGroupM2MInline]
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
            if isinstance(instance, PumpwoodPermissionPolicyGroupM2M):
                instance.updated_by = request.user
                instance.save()
            elif isinstance(instance, PumpwoodRowPermissionGroupM2M):
                instance.updated_by = request.user
                instance.save()
            elif isinstance(instance, PumpwoodUserGroupM2M):
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
