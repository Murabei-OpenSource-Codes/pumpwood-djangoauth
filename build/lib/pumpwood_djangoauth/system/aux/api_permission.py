"""Functions to help fetching permissions from user."""
import copy
import importlib.resources as pkg_resources
from typing import List, Dict, Union, Any
from django.db import connection
from django.contrib.auth import get_user_model
from pumpwood_djangoauth.config import (
    diskcache, DISKCACHE_EXPIRATION, microservice)

# Pumpwood Exceptions
from pumpwood_communication.exceptions import (
    PumpWoodActionArgsException, PumpWoodOtherException,
    PumpWoodNotImplementedError, PumpWoodObjectDoesNotExist,
    PumpWoodForbidden)

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
        'allow_any', 'is_authenticated', 'is_superuser', 'is_staff',
        'can_delete', 'can_delete_file', 'can_delete_many', 'can_list',
        'can_list_without_pag', 'can_retrieve', 'can_retrieve_file',
        'can_run_actions', 'can_save']
    """Possible roles to check for permission. This will be used to validate
       roles at `has_permission` call."""

    ACTION_ROLE_CACHE_TAG = "action-role"
    """Tag that will be used to tag action permision cache."""
    ACTION_ROLE_CACHE_TEMPLATE = "action-role--[{model_class}]"
    """Template that will be used to generate key at action permissio cache."""

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
        # Try to retrieve cache from local before retrieving action
        # data from microservice.
        dict_actions = cls._get_action_roles_cache(
            model_class=model_class)
        if dict_actions is None:
            action_list = microservice.list_actions(model_class=model_class)
            dict_actions = dict(
                [[x['action_name'],
                  x.get('permission_role', 'can_run_actions')]
                for x in action_list])

            # Set diskcache to reduce call on microservice to check for
            # action permission
            cls._set_action_roles_cache(
                model_class=model_class, action_roles=dict_actions)

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
    def _get_action_role_cache_key(cls, model_class: str) -> str:
        """Get action permission from diskcache.

        Args:
            model_class (str):
                Model class associated with action.

        Returns:
            Return key for model classe action permission roles.
        """
        return cls.ACTION_ROLE_CACHE_TEMPLATE.format(
            model_class=model_class)

    @classmethod
    def _get_action_roles_cache(cls, model_class: str) -> str:
        """Get action permission from diskcache.

        Args:
            model_class (str):
                Model class associated with action.

        Returns:
            Return a dictionary with associated roles of model_class
            actions.
        """
        key = cls._get_action_role_cache_key(model_class=model_class)
        return diskcache.get(key)

    @classmethod
    def _set_action_roles_cache(cls, model_class: str,
                                action_roles: str) -> bool:
        """Get action associated roles from diskcache.

        Args:
            model_class (str):
                Model class associated with action.
            action_roles (str):
                Association between action and roles.

        Returns:
            True if cache is set.
        """
        key = cls._get_action_role_cache_key(model_class=model_class)
        return diskcache.set(
            key=key, value=action_roles, expire=DISKCACHE_EXPIRATION,
            tag=cls.ACTION_ROLE_CACHE_TAG)

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

    HAS_PERMISSION_CACHE_TAG = "has-permission"
    """Tag used to set cache values for has permission."""

    HAS_PERMISSION_CACHE_TEMPLATE = (
        "has-permission--auth[{is_authenticated}]_r{route_id}_u[{user_id}]_" +
        "r[{role}]_a[{action}]")
    """Template used to create a key for cache."""

    @classmethod
    def get_role_options(cls):
        """Return role options."""
        return copy.deepcopy(cls.ROLE_OPTIONS)

    @classmethod
    def _get_has_permission_cache_key(cls, is_authenticated: bool,
                                      route_id: int, user_id: int, role: str,
                                      action: str) -> str:
        """Get key for cache of has permission function.

        Args:
            is_authenticated (bool):
                If user is authenticated.
            route_id (int):
                ID of the route that will be checked for authorization.
            user_id (int):
                ID of the user to check for permission.
            role (str):
                Role that will be checked for permission.
            action (str):
                Action associated with permission check.
        """
        # Set types to avoid SQL injection.
        return cls.HAS_PERMISSION_CACHE_TEMPLATE.format(
            is_authenticated=is_authenticated, route_id=route_id,
            user_id=user_id, role=role, action=action)

    @classmethod
    def _get_has_permission_cache(cls, is_authenticated: bool,
                                  route_id: int, user_id: int, role: str,
                                  action: str) -> bool:
        """Get key for cache of has permission function.

        Args:
            is_authenticated (bool):
                If user is authenticated.
            route_id (int):
                ID of the route that will be checked for authorization.
            user_id (int):
                ID of the user to check for permission.
            role (str):
                Role that will be checked for permission.
            action (str):
                Action associated with permission check.

        Returns:
            Return cached value for `has_permission` function.
        """
        key = cls._get_has_permission_cache_key(
            is_authenticated=is_authenticated, route_id=route_id,
            user_id=user_id, role=role, action=action)
        return diskcache.get(key)

    @classmethod
    def _set_has_permission_cache(cls, is_authenticated: bool,
                                  route_id: int, user_id: int, role: str,
                                  action: str, value: bool) -> bool:
        """Get key for cache of has permission function.

        Args:
            is_authenticated (bool):
                If user is authenticated.
            route_id (int):
                ID of the route that will be checked for authorization.
            user_id (int):
                ID of the user to check for permission.
            role (str):
                Role that will be checked for permission.
            action (str):
                Action associated with permission check.
            value (bool):
                Valeu to be set as cached value for `has_permission`
                function.

        Returns:
            Return `True` if cache was set.
        """
        key = cls._get_has_permission_cache_key(
            is_authenticated=is_authenticated, route_id=route_id,
            user_id=user_id, role=role, action=action)
        return diskcache.set(
            key=key, value=value, tag=cls.HAS_PERMISSION_CACHE_TAG,
            expire=DISKCACHE_EXPIRATION)

    @classmethod
    def has_permission(cls, is_authenticated: bool, route_id: int,
                       user_id: int, role: str, action: str) -> bool:
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
            user_id (int):
                ID of user object that will be checked for permision.
            role (str):
                Name of the role that is associated with the request to check
                for permission.
            action (str):
                If action, check also at action custom policies.

        Returns:
            Return a boolean value flaging if user has access to end-point/
            action.
        """
        # Allow any will always return true
        if role == 'allow_any':
            return True
        # Only allow any end-point can be used without authentication
        elif user_id is None:
            return False

        ####################################
        # Set types to avoid SQL injection #
        is_authenticated = bool(is_authenticated)
        route_id = int(route_id)
        user_id = int(user_id)

        action = "###no_action###" if action is None else action
        if role != 'can_run_actions':
            action = "###no_action###"

        # Substitute empty action values to ingect on SQL
        if ' ' in action:
            # Check for spaces to reduce SQL injection
            msg = (
                'Action [{action}] should not have spaces on name '
                'definition')
            raise PumpWoodForbidden(
                msg, payload={'action': action})

        # Use cache to avoid permission check on backend
        has_permission_cache = cls._get_has_permission_cache(
            is_authenticated=is_authenticated, route_id=route_id,
            user_id=user_id, role=role, action=action)
        if has_permission_cache is not None:
            return has_permission_cache

        User = get_user_model() # NOQA
        user = User.objects.get(id=user_id)

        # If the role is explicity set to super user and user is not
        # return False
        if not user.is_superuser and role == 'is_superuser':
            return False

        # It is not expected that any route end-point is set to allow
        # only authenticated users
        has_permission_results = None
        if user.is_superuser:
            has_permission_results = True
        elif role == 'is_authenticated':
            has_permission_results = is_authenticated
        elif role == 'is_staff':
            has_permission_results = user.is_staff
        else:
            has_permission_results = cls._get_non_general_roles(
                route_id=route_id, user_id=user.id, role=role,
                action=action)
        cls._set_has_permission_cache(
            is_authenticated=is_authenticated, route_id=route_id,
            user_id=user_id, role=role, action=action,
            value=has_permission_results)
        return has_permission_results

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
                               role: str, action: str) -> List[dict]:
        """Get non superuser permissions associated with user."""
        # Validate role option to not allow SQL injection
        cls._validate_role_options(role=role)

        # Use role to inject on query to filter the correct column
        query = route_api_permissions.format(role=role)

        # Set parameters and run query
        query_parameters = {
            "user_id": user_id, "route_id": route_id, "role": role,
            "action": action}
        with connection.cursor() as cursor:
            cursor.execute(query, query_parameters)
            rows = cursor.fetchall()

        if 1 < len(rows):
            msg = (
                "Role permission query resulted in more the one result. " +
                "This should not occour, ask tecnical team for debug and " +
                "validation.")
            raise PumpWoodOtherException(message=msg)

        # Case no permission is avaiable at database
        if len(rows) == 0:
            return False
        else:
            permission_result = rows[0][0]
            # Case case that user has other permission, but not this one
            if permission_result is None:
                return False
            else:
                return permission_result


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
        splited_path = cls._split_path(path=path)
        query_template = """
            SELECT *
            FROM public.pumpwood__route
            WHERE %(path)s LIKE route_url || '%%'
        """
        from pumpwood_djangoauth.system.models import KongRoute
        query_results = list(
            KongRoute.objects.raw(query_template, {'path': path}))
        if len(query_results) == 0:
            msg = (
                "Route with begging path [{path}] is not registered on "
                "KongRoute.\nWhen developing a new route it is necessary "
                "to build the image with it route for it to be registred "
                "before testing end-points locally.")\
                .format(path=path)
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
