from django.apps import AppConfig


class GroupsConfig(AppConfig):
    """Django App config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pumpwood_djangoauth.groups'
    verbose_name = 'User groups'
