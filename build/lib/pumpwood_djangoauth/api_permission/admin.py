from django.contrib import admin
from pumpwood_djangoauth.api_permission.models import (
    PumpwoodPermissionPolicy, PumpwoodPermissionPolicyAction,
    PumpwoodPermissionGroup, PumpwoodPermissionUserGroupM2M,
    PumpwoodPermissionPolicyGroupM2M)
from pumpwood_djangoauth.api_permission.forms import (
    PumpwoodPermissionPolicyAdminForm, PumpwoodPermissionGroupAdminForm)


class PumpwoodPermissionPolicyActionInline(admin.TabularInline):
    model = PumpwoodPermissionPolicyAction
    extra = 0
    fields = ['policy', 'action', 'permission']
    ordering = ('action', 'permission', )


class PumpwoodPermissionPolicyAdmin(admin.ModelAdmin):
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
    ]

    fieldsets = ((
             None, {
                 'fields': (
                     'description', 'notes', 'dimensions',
                     'route',
                     'updated_by',
                     'updated_at',
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
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
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
        if obj.id is None:
            return "-"
        return obj.route.route_name
    get_route_name.allow_tags = True
    get_route_name.__name__ = "Route"


admin.site.register(
    PumpwoodPermissionPolicy, PumpwoodPermissionPolicyAdmin)


class PumpwoodPermissionPolicyGroupM2MInline(admin.TabularInline):
    model = PumpwoodPermissionPolicyGroupM2M
    extra = 0
    fields = ['group', 'priority', 'general_policy', 'custom_policy', ]
    ordering = ('priority', 'general_policy', 'custom_policy__description')


class PumpwoodPermissionUserGroupM2MInline(admin.TabularInline):
    model = PumpwoodPermissionUserGroupM2M
    extra = 0
    fields = ['user', 'group', ]
    ordering = ('user__username', )


class PumpwoodPermissionGroupAdmin(admin.ModelAdmin):
    form = PumpwoodPermissionGroupAdminForm

    list_filter = []
    search_fields = ["description", "notes", ]

    list_display = ("description", "notes", )
    readonly_fields = ['updated_by', 'updated_at']

    inlines = [
        PumpwoodPermissionUserGroupM2MInline,
        PumpwoodPermissionPolicyGroupM2MInline
    ]

    fieldsets = ((
             None, {
                 'fields': (
                     'description', 'notes', 'dimensions',
                     'updated_by', 'updated_at')}
         ), (
             'Extra-info', {
                 'fields': ('extra_info', ), }

         )
    )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()

        for instance in instances:
            if isinstance(instance, PumpwoodPermissionUserGroupM2M):
                instance.updated_by = request.user
                instance.save()
            if isinstance(instance, PumpwoodPermissionPolicyGroupM2M):
                instance.updated_by = request.user
                instance.save()
            else:
                instance.save()
        formset.save_m2m()


admin.site.register(
    PumpwoodPermissionGroup, PumpwoodPermissionGroupAdmin)
