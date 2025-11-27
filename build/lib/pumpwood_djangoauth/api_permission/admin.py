"""Create admin for API permission."""
from django.contrib import admin
from pumpwood_djangoauth.api_permission.models import (
    PumpwoodPermissionPolicy, PumpwoodPermissionPolicyAction,
    PumpwoodPermissionPolicyGroupM2M, PumpwoodPermissionPolicyUserM2M)
from pumpwood_djangoauth.api_permission.forms import (
    PumpwoodPermissionPolicyAdminForm, PumpwoodPermissionPolicyActionAdminForm,
    PumpwoodPermissionPolicyGroupM2MAdminForm,
    PumpwoodPermissionPolicyUserM2MAdminForm)


class PumpwoodPermissionPolicyActionInline(admin.TabularInline):
    """Inline PumpwoodPermissionPolicyAction."""
    model = PumpwoodPermissionPolicyAction
    extra = 0
    fields = ['policy', 'action', 'is_allowed']
    ordering = ('action', 'is_allowed', )


class PumpwoodPermissionPolicyGroupM2MInline(admin.TabularInline):
    """Group permission m2m inline."""
    model = PumpwoodPermissionPolicyGroupM2M
    extra = 0
    fields = ['group', 'general_policy', 'custom_policy', ]
    ordering = ('general_policy', 'custom_policy__description')


class PumpwoodPermissionPolicyUserM2MInline(admin.TabularInline):
    """Group permission m2m inline."""
    model = PumpwoodPermissionPolicyUserM2M
    extra = 0
    fields = ['user', 'general_policy', 'custom_policy', ]
    ordering = ('general_policy', 'custom_policy__description')


@admin.register(PumpwoodPermissionPolicy)
class PumpwoodPermissionPolicyAdmin(admin.ModelAdmin):
    """Admin for PumpwoodPermissionPolicy model."""
    form = PumpwoodPermissionPolicyAdminForm

    list_filter = [
        "route__route_name", "can_list", "can_list_without_pag",
        "can_retrieve", "can_retrieve_file", "can_delete",
        "can_delete_many", "can_delete_file", "can_save",
        "can_run_actions"]
    search_fields = ['description', ]

    list_display = (
        "description", "get_route_name", "can_list", "can_list_without_pag",
        "can_retrieve", "can_retrieve_file", "can_delete",
        "can_delete_many", "can_delete_file", "can_save",
        "can_run_actions", )
    readonly_fields = ['updated_by', 'updated_at']

    inlines = [
        PumpwoodPermissionPolicyActionInline,
        PumpwoodPermissionPolicyUserM2MInline,
        PumpwoodPermissionPolicyGroupM2MInline]

    fieldsets = ((
             None, {
                 'fields': (
                     'description', 'notes', 'dimensions',
                     'route', 'updated_by', 'updated_at',
                 )}
         ), (
             'Permissions', {
                 'fields': (
                     "can_list", "can_list_without_pag",
                     'can_retrieve', 'can_retrieve_file',
                     'can_delete', 'can_delete_many',
                     'can_delete_file', 'can_save',
                     'can_run_actions',), }

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
            if isinstance(instance, PumpwoodPermissionPolicyAction):
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


@admin.register(PumpwoodPermissionPolicyAction)
class PumpwoodPermissionPolicyActionAdmin(admin.ModelAdmin):
    """Admin for PumpwoodPermissionPolicy model."""
    form = PumpwoodPermissionPolicyActionAdminForm
    list_display = (
        "policy", "policy__route", "action", "is_allowed", "updated_by",
        "updated_at", )
    list_filter = [
        "policy", "policy__route", "action", "is_allowed"]
    search_fields = []
    readonly_fields = ['updated_by', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Save model add updated_by field."""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PumpwoodPermissionPolicyGroupM2M)
class PumpwoodPermissionPolicyGroupM2MAdmin(admin.ModelAdmin):
    """Admin for PumpwoodPermissionPolicy model."""
    form = PumpwoodPermissionPolicyGroupM2MAdminForm
    list_display = (
        "group", "general_policy", "custom_policy", "updated_by",
        "updated_at", )
    list_filter = [
        "group", "general_policy", "custom_policy"]
    search_fields = []
    readonly_fields = ['updated_by', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Save model add updated_by field."""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PumpwoodPermissionPolicyUserM2M)
class PumpwoodPermissionPolicyUserM2MAdmin(admin.ModelAdmin):
    """Admin for PumpwoodPermissionPolicy model."""
    form = PumpwoodPermissionPolicyUserM2MAdminForm
    list_display = (
        "user", "general_policy", "custom_policy", "updated_by",
        "updated_at", )
    list_filter = [
        "user", "general_policy", "custom_policy"]
    search_fields = []
    readonly_fields = ['updated_by', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Save model add updated_by field."""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
