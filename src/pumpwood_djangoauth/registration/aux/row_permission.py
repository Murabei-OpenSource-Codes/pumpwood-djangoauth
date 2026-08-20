"""Helpers to resolve effective row permissions for a user."""
import importlib.resources as pkg_resources
from typing import List


# Read sql query from package resources
sql_content = pkg_resources.read_text(
    'pumpwood_djangoauth.registration.aux.query',
    'group_user_row_permissions.sql')


class RowPermissionAux:
    """Auxiliary class to fetch user row permissions."""

    @classmethod
    def get(cls, user, request) -> List[dict]:
        """Get user row permissions, including self and group related.

        Args:
            user (User):
                User object to fetch associated permissions.
            request:
                Django request used for serializer context.

        Returns:
            List[dict]:
                Serialized row-permission records.
        """
        if user.is_superuser:
            return cls._get_superuser(request=request)
        else:
            return cls._get_non_superuser(user=user, request=request)

    @classmethod
    def _get_superuser(cls, request) -> List[dict]:
        """Return row permissions visible to a superuser.

        Simulates full access by serializing every row-permission record.
        These records are not persisted for the superuser in the database.

        Args:
            request:
                Django request used for serializer context.

        Returns:
            List[dict]:
                Serialized row-permission records.
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
        """Return row permissions for a non-superuser.

        Args:
            user (User):
                User whose row permissions are resolved.
            request:
                Django request used for serializer context.

        Returns:
            List[dict]:
                Serialized row-permission records from direct and group
                links.
        """
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
