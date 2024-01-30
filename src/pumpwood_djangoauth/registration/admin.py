from django.contrib import admin

# Register your models here.
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


##############
# User Admin #
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
