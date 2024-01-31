from django.contrib import admin
from django.contrib import messages
from pumpwood_djangoauth.registration.models import (
    UserProfile, PumpwoodMFAMethod, PumpwoodMFAToken, PumpwoodMFACode,
    PumpwoodMFARecoveryCode)
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


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
        "msg"]


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets
    inlines = UserAdmin.inlines + [
        UserProfileInline, PumpwoodMFAMethodInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, PumpwoodMFAMethod):
                print("before instance:", instance)
                # Do something with `instance`
                instance.save()
                print("after instance.is_validated:", instance.is_validated)
                if not instance.is_validated:
                    msg = (
                        "O MFA {type} {mfa_parameter} não pode ser validado "
                        "e não será utilizado para validação do login").format(
                            type=instance.type,
                            mfa_parameter=instance.mfa_parameter)
                    messages.error(request, msg)
            else:
                print("not PumpwoodMFAMethod")
        super().save_formset(request, form, formset, change)

##############
# User Admin #
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
