"""Django application configuration for Pumpwood Auth."""
import os
import sys
from django.apps import AppConfig


class PumpwoodDjangoauthConfig(AppConfig):
    """Pumpwood Django Auth application config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pumpwood_djangoauth'

    def ready(self):
        """Initialize singletons for non-gunicorn runtimes."""
        print("ready")
