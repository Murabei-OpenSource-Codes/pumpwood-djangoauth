from django.contrib import admin

# Register your models here.
from pumpwood_djangoauth.registration.models import (
    UserProfile, PumpwoodMFAMethod, PumpwoodMFAToken, PumpwoodMFACode,
    PumpwoodMFARecoveryCode)
from pumpwood_djangoauth.registration.forms import MFAAuthenticationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView


######################
# Customn User Admin #
class UserProfileInline(admin.TabularInline):
    model = UserProfile


class PumpwoodMFAMethodInline(admin.TabularInline):
    model = PumpwoodMFAMethod
    extra = 0
    read_only = ['is_validated']


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


#######################
# User Admin with MFA #
class CustomAdmin(admin.AdminSite):
    login_template = "custom_login.html"
    form_class = MFAAuthenticationForm

    # def login(self, request, extra_context=None):
    #     if request.method != "POST":
    #         return (LoginView.as_view(template_name=self.login_template)
    #                 (request, extra_context))
    #     else:
    #         print("\n\n\n\nrequest.POST:", request.POST)
    #         print("\n\n\n\n")
    #         return (LoginView.as_view(template_name=self.login_template)
    #                 (request, extra_context))

    def recheio_do_andre(self, request, extra_content=None):
        return True

admin.site.__class__ = CustomAdmin
