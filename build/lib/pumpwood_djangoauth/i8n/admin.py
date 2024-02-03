"""Register I8n translations."""
from django.contrib import admin
from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation


class PumpwoodI8nTranslationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "sentence", "tag", "plural", "language", "user_type",
        "translation")
    search_fields = ('sentence', "translation")
    list_filter = ["tag", "plural", "language", "user_type"]


##############
# User Admin #
admin.site.register(PumpwoodI8nTranslation, PumpwoodI8nTranslationAdmin)
