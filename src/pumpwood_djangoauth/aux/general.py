"""General auxiliary functions for Pumpwood Django Auth."""
import django


def django_apps_ready() -> bool:
    """Check if Django apps are ready."""
    try:
        from django.apps import apps
        return apps.ready
    except Exception:
        return False

