from django.contrib import admin

# Register your models here.
from .models import UserProfile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


######################
# Customn User Admin #
class UserProfileInline(admin.TabularInline):
    model = UserProfile


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets
    inlines = UserAdmin.inlines + [UserProfileInline, ]
######################


##############
# User Admin #
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
