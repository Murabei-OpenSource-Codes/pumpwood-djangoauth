"""Functions to help fetching permissions from user."""
import copy
import importlib.resources as pkg_resources
from typing import List, Dict, Union, Any
from django.db import connection
from pumpwood_djangoauth.config import (
    diskcache, DISKCACHE_EXPIRATION, microservice)

# Pumpwood Exceptions
from pumpwood_communication.exceptions import (
    PumpWoodActionArgsException, PumpWoodOtherException,
    PumpWoodNotImplementedError, PumpWoodObjectDoesNotExist)

# Read sql query from package resources
route_api_permissions = pkg_resources.read_text(
    'pumpwood_djangoauth.system.aux.query',
    'route_api_permissions.sql')


def _get_item_or_none(list_data: list, index: int) -> Union[None, Any]:
    """Get an item from a list or return None if index greater than lenght.

    Args:
        list_data (list):
            Data on a list format.
        index (int):
            Index of the data to get from list.

    Returns:
        Return the element list_data[index] if index < lenght and None
        otherwise.
    """
    return list_data[index] if index < len(list_data) else None


class MapPathRoleAux:
    """Class to help mapping http calls to Pumpwood end-points."""

    ENDPOINT_OPTIONS = [
        'list', 'list-without-pag', 'retrieve',
        'retrieve-file', 'delete', 'remove-file-field',
        'delete-field', 'save', 'actions', 'options', 'list-options',
        'retrieve-options', 'aggregate', 'pivot', 'bulk-save']
    """Possible end-points on Pumpwood default routes."""
    METHOD_OPTIONS = ['get', 'post', 'delete']
    """Possible methods that are implemented on PumpWood."""

    ROLE_OPTIONS = [
        'allow_any', 'is_authenticated', 'is_staff', 'can_delete',
        'can_delete_file', 'can_delete_many', 'can_list',
        'can_list_without_pag', 'can_retrieve', 'can_retrieve_file',
        'can_run_actions', 'can_save']
    """Possible roles to check for permission. This will be used to validate
       roles at `has_permission` call."""

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
    def _get_action_permission(cls, model_class: str, action: str) -> str:
        """Get action permission_role."""
        action_list = microservice.list_actions(model_class=model_class)
        dict_actions = dict(
            [[x['action_name'], x.get('permission_role', 'can_run_actions')]
            for x in action_list])
        print('dict_actions:', dict_actions)
        if action not in dict_actions.keys():
            msg = (
                "Action [{action}] was is not avaiable at " +
                "model_class[{model_class}]. Call list actions to verify " +
                "the possible actions and its arguments.")
            raise PumpWoodObjectDoesNotExist(
                msg, payload={'action': action, 'model_class': model_class})

        permission_role = dict_actions.get(action)
        return permission_role

    @classmethod
    def get_role_options(cls) -> List[str]:
        """Get role options."""
        return copy.deepcopy(cls.ROLE_OPTIONS)

    @classmethod
    def get_endpoint_options(cls) -> List[str]:
        """Get endpoint options."""
        return copy.deepcopy(cls.ENDPOINT_OPTIONS)

    @classmethod
    def map(cls, route, method: str, model_class: str, endpoint: str,
            action: str) -> str:
        """Map endpoint/method to Pumpwood roles.

        Args:
            route (KongRoute):
                Kong route object.
            method (str):
                Method to map to Pumpwood roles.
            model_class (str):
                pass
            endpoint (str):
                pass
            action (str):
                pass

        Returns:
            Pumpwood `role`, `model_class`, `endpoint` and `action` associated
            with method and path.
        """
        # According to `route_type` set the expected role, in some cases
        # it is expected to have custom implemention for some endpoints
        if route.route_type in ['aux', 'gui', 'datavis']:
            return {
                'role': 'can_retrieve',
                'type': route.route_type,
                'model_class': model_class,
                'endpoint': endpoint,
                'action': action, }
        if route.route_type in ['media']:
            return {
                'role': 'can_retrieve_file',
                'type': route.route_type,
                'model_class': model_class,
                'endpoint': endpoint,
                'action': action, }
        # Static files should be avaiable to all users
        if route.route_type in ['static']:
            return {
                'role': 'allow_any',
                'type': route.route_type,
                'model_class': model_class,
                'endpoint': endpoint,
                'action': action, }
        # Admin urls are avaiable only to staff associated users
        if route.route_type in ['admin']:
            return {
                'role': 'is_staff',
                'type': route.route_type,
                'model_class': model_class,
                'endpoint': endpoint,
                'action': action, }

        # It should only remain the 'endpoint' options on `route_type`
        if route.route_type != 'endpoint':
            msg = (
                "Route type [{route_type}] not implemented yet")\
                .format(route_type=route.route_type)
            raise PumpWoodActionArgsException(message=msg)

        # Validate method arguments
        role = None
        method_lower = method.lower()
        cls._validate_endpoint_options(endpoint=endpoint)
        cls._validate_method_options(method=method_lower)
        if endpoint == 'list':
            role = 'can_list'
        elif endpoint == 'aggregate':
            role = 'can_list'
        elif endpoint == 'list-without-pag':
            role = 'can_list_without_pag'
        elif endpoint == 'pivot':
            role = 'can_list_without_pag'

        # Retrieve
        elif endpoint == 'retrieve':
            role = 'can_retrieve'
        elif endpoint == 'retrieve-file':
            role = 'can_retrieve_file'

        # Delete
        elif endpoint == 'delete':
            if method_lower == 'get':
                msg = 'Endpoint delete and method get is not implemented'
                raise PumpWoodNotImplementedError(message=msg)
            elif method_lower == 'delete':
                role = 'can_delete'
            else:
                role = 'can_delete_many'
        elif endpoint == 'remove-file-field':
            role = 'can_delete_file'
        elif endpoint == 'delete-file':
            role = 'can_delete_file'

        # Save end-points
        elif endpoint == 'save':
            role = 'can_save'
        elif endpoint == 'bulk-save':
            role = 'can_save'

        # Actions
        elif endpoint == 'actions':
            if method_lower == 'get':
                role = 'is_authenticated'
            elif method_lower == 'post':
                role = cls._get_action_permission(
                    model_class=model_class, action=action)
            else:
                msg = "Action end-point does not permit delete method"
                raise PumpWoodActionArgsException(message=msg)

        # Options
        elif endpoint == 'options':
            if method_lower == 'get':
                role = 'can_list'
            elif method_lower == 'post':
                role = 'can_save'
            else:
                msg = "Options end-point does not permit delete method"
                raise PumpWoodActionArgsException(message=msg)

        elif endpoint == 'list-options':
            role = 'can_list'

        elif endpoint == 'retrieve-options':
            if method_lower == 'get':
                role = 'can_retrieve'
            elif method_lower == 'post':
                role = 'can_save'
            else:
                msg = "Options end-point does not permit delete method"
                raise PumpWoodActionArgsException(message=msg)

        return {
            'role': role,
            'type': route.route_type,
            'model_class': model_class,
            'endpoint': endpoint,
            'action': action, }


class RouteAPIPermissionAux:
    """Auxiliary class to check user's permissions for a route."""
    @classmethod
    def get_role_options(cls):
        """Return role options."""
        return copy.deepcopy(cls.ROLE_OPTIONS)

    @classmethod
    def has_permission(cls, is_authenticated: bool, route_id: int, user,
                       role: str) -> bool:
        """Get user permission, including self and group related.

        It is considered that the URL paths follow de default pattern of
        Pumpowood: `/{type}/{model_class}/{endpoint}/{action}`. Paths
        `endpoint` and `action` might be optional.

        When `type` is different from `rest`, can_retrieve is the role
        expected.

        It is possible due to custom implementation that
        non `endpoint` routes have specific roles, check the error msgs if
        necessary.

        Args:
            is_authenticated (bool):
                Boolean value indicating if request is authenticated.
            route_id (KongRoute):
                KongRoute id that will be checked for permision.
            user (User):
                User object that will be checked for permision.
            role (str):
                Name of the role that is associated with the request to check
                for permission.

        Returns:
            Return a boolean value flaging if user has access to end-point/
            action.
        """
        # It is not expected that any route end-point is set to allow
        # only authenticated users
        if user.is_superuser:
            print('user.is_superuser')
            return True
        if role == 'allow_any':
            print('allow_any')
            return True
        if role == 'is_authenticated':
            print('is_authenticated')
            return is_authenticated
        if role == 'is_staff':
            print('is_staff')
            return user.is_staff
        else:
            print('_get_non_general_roles')
            return cls._get_non_general_roles(
                route_id=route_id, user_id=user.id, role=role)

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
        role_options = MapPathRoleAux.get_role_options()
        if role not in role_options:
            msg = (
                "Role is not at possible options [{role}]. Possible options "
                "{role_options}").format(
                    role=role, role_options=role_options)
            raise PumpWoodActionArgsException(
                message=msg, payload={"role": "Not in possible options"})

    @classmethod
    def _get_non_general_roles(cls, route_id: int, user_id: int,
                               role: str) -> List[dict]:
        """Get non superuser permissions associated with user."""
        # Validate role option to not allow SQL injection
        cls._validate_role_options(role=role)
        route_id = int(route_id)
        user_id = int(user_id)

        # Use role to inject on query to filter the correct column
        query = route_api_permissions.format(role=role)

        # Set parameters and run query
        query_parameters = {
            "user_id": user_id, "route_id": route_id, "role": role}
        with connection.cursor() as cursor:
            cursor.execute(query, query_parameters)
            rows = cursor.fetchall()

        print('rows:', rows)
        if len(rows) == 0:
            return False

        if 1 < len(rows):
            msg = (
                "Role permission query resulted in more the one result. " +
                "This should not occour, ask tecnical team for debug and " +
                "validation.")
            raise PumpWoodOtherException(message=msg)
        return rows[0][0]


class GetRouteAux:
    """Class to help get route using differente methods."""

    @classmethod
    def from_path(cls, path: str):
        """Get route from path.

        Return route that correponds to the begging of the path.

        Args:
            path (str):
                Path used at the query.

        Returns:
            A KongRoute object with path correspondent to the start the path
            of the function argument.
        """
        query_template = """
            SELECT *
            FROM public.pumpwood__route
            WHERE %(path)s LIKE route_url || '%%'
        """
        from pumpwood_djangoauth.system.models import KongRoute
        query_results = list(
            KongRoute.objects.raw(query_template, {'path': path}))
        if len(query_results) == 0:
            msg = "Route with begging path [{path}] not found".format(
                path=path)
            raise PumpWoodObjectDoesNotExist(message=msg)
        elif 1 < len(query_results):
            routes_returned = '\n'.join([r.route_url for r in query_results])
            msg = (
                "More than one route was returned with begging path " +
                "[{path}] validate the path and try again. " +
                "Routes returned:\n" "{routes}")\
                .format(routes=routes_returned, path=path)
            raise PumpWoodObjectDoesNotExist(message=msg)

        route = query_results[0]
        splited_path = cls._split_path(path=path)
        splited_path['route'] = route
        return splited_path

    @classmethod
    def _split_path(cls, path: str) -> Dict[str, str]:
        """Split path retrieving model_class, endpoint and action if present.

        Args:
            path (str):
                Path to retrieve path components.

        Returns:
            Return a dict with path components.
        """
        if path[0] != "/":
            path = "/" + path
        path_splited = path.split("/", maxsplit=5)
        type = _get_item_or_none(list_data=path_splited, index=1)
        model_class = _get_item_or_none(list_data=path_splited, index=2)
        endpoint = _get_item_or_none(list_data=path_splited, index=3)
        action = _get_item_or_none(list_data=path_splited, index=4)
        return {
            'type': type, 'model_class': model_class,
            'endpoint': endpoint, 'action': action}
