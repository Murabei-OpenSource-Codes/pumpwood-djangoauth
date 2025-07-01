"""Admin for registration models."""
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from pumpwood_djangoauth.registration.models import (
    UserProfile, PumpwoodMFAMethod)
from pumpwood_djangoauth.api_permission.models import (
    PumpwoodPermissionPolicyUserM2M)
from pumpwood_djangoauth.groups.models import (
    PumpwoodUserGroupM2M)


######################
# Customn User Admin #
class UserProfileInline(admin.TabularInline):
    """User Profile Inline."""
    model = UserProfile


class PumpwoodMFAMethodInline(admin.TabularInline):
    """Pumpwood MFA Method Inline."""
    model = PumpwoodMFAMethod
    extra = 0
    readonly_fields = ('is_validated', 'msg')
    fields = [
        "is_enabled", "is_validated", "priority", "type", "mfa_parameter",
        "extra_info", "msg"]


class PumpwoodPermissionPolicyUserM2MInline(admin.TabularInline):
    """Pumpwood Permission Policy User M2M Inline."""
    model = PumpwoodPermissionPolicyUserM2M
    fk_name = 'user'
    extra = 0
    fields = [
        'user', 'general_policy', 'custom_policy',
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


class PumpwoodUserGroupM2MInline(admin.TabularInline):
    """Pumpwood Permission Policy Group M2M Inline."""
    model = PumpwoodUserGroupM2M
    fk_name = 'user'
    extra = 0
    fields = ['group']
    ordering = ('group__description', )


class CustomUserChangeForm(UserChangeForm):
    """Custom User Change Form."""
    class Meta(UserChangeForm.Meta):
        """Meta."""
        model = User


class CustomUserAdmin(UserAdmin):
    """Custom User Admin."""
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets
    inlines = UserAdmin.inlines + (
        UserProfileInline, PumpwoodMFAMethodInline,
        PumpwoodPermissionPolicyUserM2MInline,
        PumpwoodUserGroupM2MInline)
    list_display = (
        "id", "username", "email", "is_staff", "is_superuser", "get_has_mfa",
        "get_is_service_user")
    ordering = ["id"]

    def save_formset(self, request, form, formset, change):
        """Super save_formset."""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, PumpwoodMFAMethod):
                # Do something with `instance`
                instance.save()
                if not instance.is_validated:
                    msg = (
                        "O MFA {type} {mfa_parameter} não pode ser validado "
                        "e não será utilizado para validação do login").format(
                            type=instance.type,
                            mfa_parameter=instance.mfa_parameter)
                    messages.error(request, msg)
            if isinstance(instance, PumpwoodPermissionPolicyUserM2M):
                instance.updated_by = request.user
            if isinstance(instance, PumpwoodUserGroupM2MInline):
                instance.updated_by = request.user
            else:
                instance.save()
        super().save_formset(request, form, formset, change)

    def get_has_mfa(self, obj=None):
        """Get is user has MFA configured."""
        return obj.mfa_method_set.count() != 0
    get_has_mfa.boolean = True
    get_has_mfa.__name__ = "Has MFA configured?"

    def get_is_service_user(self, obj=None):
        """Get if user is a service user."""
        return obj.user_profile.is_service_user != 0
    get_is_service_user.boolean = True
    get_is_service_user.__name__ = "Is service user?"


##############
# User Admin #
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
