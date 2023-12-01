from django.contrib import admin
from pumpwood_djangoauth.metabase.models import (
    MetabaseDashboard, MetabaseDashboardParameter)
from pumpwood_djangoauth.metabase.forms import MetabaseDashboardForm


class MetabaseDashboardParameterInline(admin.TabularInline):
    model = MetabaseDashboardParameter
    extra = 0
    fields = [
        "dashboard", "type", "name", "notes", "default_value"]
    ordering = ('name', )


class MetabaseDashboardAdmin(admin.ModelAdmin):
    form = MetabaseDashboardForm

    list_display = (
        "id", "status", "metabase_id", "alias", "description", "notes",
        "updated_by", "updated_at")
    readonly_fields = ['updated_by', 'updated_at']

    inlines = [
        MetabaseDashboardParameterInline,
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


##############
# User Admin #
admin.site.register(MetabaseDashboard, MetabaseDashboardAdmin)
