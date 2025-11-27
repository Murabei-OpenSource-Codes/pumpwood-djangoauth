"""Register I8n translations."""
from django.contrib import admin
from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation


class PumpwoodI8nTranslationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "sentence", "tag", "plural", "language", "user_type",
        "do_not_remove", "translation")
    search_fields = ('sentence', "translation", "tag")
    list_filter = ["tag", "plural", "language", "user_type"]
    read_only = ["last_used_at"]


##############
# User Admin #
admin.site.register(PumpwoodI8nTranslation, PumpwoodI8nTranslationAdmin)
