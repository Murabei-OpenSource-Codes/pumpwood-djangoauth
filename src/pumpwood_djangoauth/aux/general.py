"""General auxiliary functions for Pumpwood Django Auth."""
import django


def django_apps_ready() -> bool:
    """Check whether Django application registry is ready.

    Returns:
        bool:
            ``True`` when Django apps are loaded, otherwise ``False``.
    """
    try:
        from django.apps import apps
        return apps.ready
    except Exception:
        return False

