"""Functions to help fetching permissions from user."""
import importlib.resources as pkg_resources
from typing import List


# Read sql query from package resources
sql_content = pkg_resources.read_text(
    'pumpwood_djangoauth.registration.aux.query',
    'group_user_row_permissions.sql')


class RowPermissionAux:
    """Auxiliary class to fetch user's permissions."""

    @classmethod
    def get(cls, user, request):
        """Get user permission, including self and group related.

        Args:
            user (User):
                User object to fetch associated permissions.
            request:
                Django request.
        """
        if user.is_superuser:
            return cls._get_superuser(request=request)
        else:
            return cls._get_non_superuser(user=user, request=request)

    @classmethod
    def _get_superuser(cls, request) -> List[dict]:
        """Return permissions of a superuser.

        It will simulate allow permission from all routes, but they will be not
        present on database

        Args:
            request:
                Django request.
        """
        from pumpwood_djangoauth.row_permission.models import (
            PumpwoodRowPermission)
        from pumpwood_djangoauth.row_permission.serializers import (
            SerializerPumpwoodRowPermission)
        query_result = PumpwoodRowPermission.objects.all()
        return SerializerPumpwoodRowPermission(
            query_result, many=True, default_fields=True,
            context={'request': request}).data

    @classmethod
    def _get_non_superuser(cls, user, request) -> List[dict]:
        """Get non superuser permissions associated with user."""
        from pumpwood_djangoauth.row_permission.models import (
            PumpwoodRowPermission)
        from pumpwood_djangoauth.row_permission.serializers import (
            SerializerPumpwoodRowPermission)

        query_parameters = {"user_id": user.id}
        query_result = PumpwoodRowPermission.objects.raw(
            sql_content, query_parameters)
        return SerializerPumpwoodRowPermission(
            query_result, many=True, default_fields=True,
            context={'request': request}).data
