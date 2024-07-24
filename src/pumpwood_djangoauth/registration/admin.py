from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from pumpwood_djangoauth.registration.models import (
    UserProfile, PumpwoodMFAMethod, PumpwoodMFAToken, PumpwoodMFACode,
    PumpwoodMFARecoveryCode)
from pumpwood_djangoauth.api_permission.models import (
    PumpwoodPermissionPolicyUserM2M)


######################
# Customn User Admin #
class UserProfileInline(admin.TabularInline):
    model = UserProfile


class PumpwoodMFAMethodInline(admin.TabularInline):
    model = PumpwoodMFAMethod
    extra = 0
    readonly_fields = ('is_validated', 'msg')
    fields = [
        "is_enabled", "is_validated", "priority", "type", "mfa_parameter",
        "extra_info", "msg"]


class PumpwoodPermissionPolicyGroupM2MInline(admin.TabularInline):
    model = PumpwoodPermissionPolicyUserM2M
    fk_name = 'user'
    extra = 0
    fields = ['user', 'priority', 'general_policy', 'custom_policy', ]
    ordering = ('priority', 'general_policy', 'custom_policy__description')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets
    inlines = UserAdmin.inlines + [
        UserProfileInline, PumpwoodMFAMethodInline,
        PumpwoodPermissionPolicyGroupM2MInline]
    list_display = (
        "id", "username", "email", "is_staff", "is_superuser", "get_has_mfa",
        "get_is_service_user")
    ordering = ["id"]

    def save_formset(self, request, form, formset, change):
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
            else:
                instance.save()
        super().save_formset(request, form, formset, change)

    def get_has_mfa(self, obj=None):
        return obj.mfa_method_set.count() != 0
    get_has_mfa.boolean = True
    get_has_mfa.__name__ = "Has MFA configured?"

    def get_is_service_user(self, obj=None):
        return obj.user_profile.is_service_user != 0
    get_is_service_user.boolean = True
    get_is_service_user.__name__ = "Is service user?"


##############
# User Admin #
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
