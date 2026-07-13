"""Django application configuration for Pumpwood Auth."""
from django.apps import AppConfig


class PumpwoodDjangoAuthConfig(AppConfig):
    """Pumpwood Django Auth application config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pumpwood_djangoauth'

    def ready(self):
        """Run application startup hooks.

        Lazy singletons from ``config`` are created on first access. When
        using gunicorn with ``--preload``, call
        ``reset_config_singletons()`` from a ``post_fork`` hook instead of
        initializing clients here.
        """
        pass