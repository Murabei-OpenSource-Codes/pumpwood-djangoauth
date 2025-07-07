"""Functions to help fetching permissions from user."""
import importlib.resources as pkg_resources
from typing import List
from django.db import connection

# Pumpwood Exceptions
from pumpwood_communication.exceptions import (
    PumpWoodActionArgsException, PumpWoodOtherException,
    PumpWoodNotImplementedError)

# Read sql query from package resources
route_api_permissions = pkg_resources.read_text(
    'pumpwood_djangoauth.system.aux.query',
    'route_api_permissions.sql')


class RouteAPIPermissionAux:
    """Auxiliary class to check user's permissions for a route."""

    ROLE_OPTIONS = [
        'can_delete', 'can_delete_file', 'can_delete_many', 'can_list',
        'can_list_without_pag', 'can_retrieve', 'can_retrieve_file',
        'can_run_actions', 'can_save']
    """Possible roles to check for permission. This will be used to validate
       roles at `has_permission` call."""

    @classmethod
    def has_permission(cls, route_id: int, user: int,
                       role: str) -> bool:
        """Get user permission, including self and group related.

        Args:
            route_id (int):
                Id of the route to check for permission.
            user (int):
                User object.
            role (str):
                HTTP method associated with request.
        """
        if user.is_superuser:
            return cls._get_superuser()
        else:
            return cls._get_non_superuser(
                user=user, route_id=route_id, role=role)

    @classmethod
    def _get_superuser(cls) -> bool:
        """Return permissions of a superuser.

        It will simulate allow permission from all routes and end-points.
        """
        return True

    @classmethod
    def _validate_role_options(cls, role: str) -> None:
        """Return the name of the permission by endpoint and method.

        Args:
            role (str):
                Role to validate.

        Raises:
            PumpWoodActionArgsException:
                Raise if role is not in `cls.ROLE_OPTIONS`.
        """
        if role not in cls.ROLE_OPTIONS:
            msg = (
                "Role is not at possible options [{role}]. Possible options "
                "{role_options}").format(
                    role=role, role_options=cls.ROLE_OPTIONS)
            raise PumpWoodActionArgsException(
                message=msg, payload={"role": "Not in possible options"})

    @classmethod
    def _get_non_superuser(cls, user, route_id: int, role: str) -> List[dict]:
        """Get non superuser permissions associated with user."""
        # Validate role option to not allow SQL injection
        cls._validate_role_options(role=role)
        route_id = int(route_id)

        # Use role to inject on query to filter the correct column
        query = route_api_permissions.format(role=role)

        # Set parameters and run query
        query_parameters = {
            "user_id": user.id, "route_id": route_id, "role": role}
        with connection.cursor() as cursor:
            cursor.execute(query, query_parameters)
            rows = cursor.fetchall()

        if len(rows) == 1:
            return rows[0][0]
        if len(rows) == 0:
            return False
        else:
            msg = (
                "Role permission query resulted in more the one result. " +
                "This should not occour, ask tecnical team for debug and " +
                "validation.")
            raise PumpWoodOtherException(message=msg)


class MapHttpCallRoleAux:
    """Class to help mapping http calls to Pumpwood end-points."""

    ENDPOINT_OPTIONS = [
        'list', 'list-without-pag', 'retrieve',
        'retrieve-file', 'delete', 'remove-file-field',
        'delete-field', 'save', 'actions', 'options', 'list-options',
        'retrieve-options', 'aggregate', 'pivot', 'bulk-save']
    METHOD_OPTIONS = ['get', 'post', 'delete']

    @classmethod
    def _validate_endpoint_options(cls, endpoint: str) -> bool:
        """Check if endpoint is implemented.

        Args:
            endpoint (str):
                Endpoint to check in expected values.

        Returns:
            Return True if in expected endpoint values.
        """
        if endpoint not in cls.ENDPOINT_OPTIONS:
            msg = (
                "Endpoint not implemented [{endpoint}]. Must be in " +
                "{options}").format(
                    endpoint=endpoint, options=cls.ENDPOINT_OPTIONS)
            raise PumpWoodNotImplementedError(msg)

    @classmethod
    def _validate_method_options(cls, method: str):
        """Check if methdod is implemented."""
        if method not in cls.METHOD_OPTIONS:
            msg = (
                "Method not implemented [{method}]. Must be in " +
                "{options}").format(
                    endpoint=method, options=cls.METHOD_OPTIONS)
            raise PumpWoodNotImplementedError(msg)

    @classmethod
    def map(cls, endpoint: str, method: str) -> str:
        """Map endpoint/method to Pumpwood roles.

        Args:
            endpoint (str):
                Endpoint to map to Pumpowood roles.
            method (str):
                Method to map to Pumpwood roles.

        Returns:
            Pumpwood role associated with endpoint/method.
        """
        method_lower = method.lower()

        # Validate method arguments
        cls._validate_endpoint_options(endpoint=endpoint)
        cls._validate_method_options(method=method_lower)

        # Map HTTP endpoint/method call.
        # List end-points
        if endpoint == 'list':
            return 'can_list'
        if endpoint == 'aggregate':
            return 'can_list'
        if endpoint == 'list-without-pag':
            return 'can_list_without_pag'
        if endpoint == 'pivot':
            return 'can_list_without_pag'

        # Retrieve
        if endpoint == 'retrieve':
            return 'can_retrieve'
        if endpoint == 'retrieve-file':
            return 'can_retrieve_file'

        # Delete
        if endpoint == 'delete':
            if method_lower == 'get':
                msg = 'Endpoint delete and method get is not implemented'
                raise PumpWoodNotImplementedError(message=msg)
            elif method_lower == 'delete':
                return 'can_delete'
            else:
                return 'can_delete_many'
        if endpoint == 'remove-file-field':
            return 'can_delete_file'
        if endpoint == 'delete-file':
            return 'can_delete_file'

        # Save end-points
        if endpoint == 'save':
            return 'can_save'
        if endpoint == 'bulk-save':
            return 'can_save'

        # Actions
        if endpoint == 'actions':
            return 'can_run_actions'

        # Options
        if endpoint == 'options':
            return 'can_list'
        if endpoint == 'list-options':
            return 'can_list'
        if endpoint == 'retrieve-options':
            return 'can_retrieve'
