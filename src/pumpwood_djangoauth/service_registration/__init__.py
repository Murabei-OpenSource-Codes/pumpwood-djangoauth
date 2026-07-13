"""Default Kong service and route definitions for the auth application.

Use ``get_service_definitions`` to obtain ready-made service and route
dictionaries for ``register_auth_kong_objects``.
"""
from .definition import get_service_definitions

__docformat__ = "google"
__all__ = [get_service_definitions, ]
