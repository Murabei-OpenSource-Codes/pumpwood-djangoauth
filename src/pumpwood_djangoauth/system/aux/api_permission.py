"""Functions to help fetching permissions from user."""
import copy
import importlib.resources as pkg_resources
from dataclasses import dataclass
from typing import List, Dict, Union, Any
from django.db import connection
from django.contrib.auth import get_user_model
from pumpwood_djangoviews.app import PumpwoodDjangoAppInspect
from pumpwood_djangoauth.config import microservice, TOKEN_CACHE_EXPIRATION

# Pumpwood Exceptions
from pumpwood_communication.exceptions import (
    PumpWoodActionArgsException, PumpWoodOtherException,
    PumpWoodNotImplementedError, PumpWoodObjectDoesNotExist,
    PumpWoodForbidden)
from pumpwood_communication.cache import default_cache
from pumpwood_communication.type import PumpwoodDataclassMixin


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


@dataclass
class PumpwoodAuthActionRoleCache(PumpwoodDataclassMixin):
    """Cache for Pumpwood permission."""

    model_class: str
    """Model class to check for permission."""
    context: str = "pumpwood_djangoauth__action_role"
    """Context for the cache key."""


@dataclass
class PumpwoodAuthHasPermissionCache(PumpwoodDataclassMixin):
    """Cache entry for route permission checks."""

    is_authenticated: bool
    """Whether the request is authenticated."""
    route_id: int
    """Kong route primary key."""
    user_id: int
    """User primary key."""
    role: str
    """Role being validated."""
    action: str
    """Action being validated."""
    context: str = "pumpwood_djangoauth__has_permission"
    """Context for the cache key."""


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
        'is_service_user', 'can_delete', 'can_delete_file',
        'can_delete_many', 'can_list', 'can_list_without_pag', 'can_retrieve',
        'can_retrieve_file', 'can_run_actions', 'can_save']
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
        hash_dict = PumpwoodAuthActionRoleCache(model_class=model_class)
        dict_actions = default_cache.get(hash_dict=hash_dict)
        if dict_actions is None:
            # Fetch locally the actions and permissions
            action_list = PumpwoodDjangoAppInspect\
                .list_actions_local(model_class=model_class)
            if action_list is None:
                # If not found locally, try to fetch from microservice
                action_list = microservice.list_actions(
                    model_class=model_class)
                
                # If it is not found 
                if action_list is None:
                    msg = (''
                        "It was not possible to retrieve actions and "
                        "permissions for model_class[{model_class}]. Check "
                        "if it was registered on Pumpwood.")
                    raise PumpWoodObjectDoesNotExist(
                        msg, payload={
                            'action': action, 'model_class': model_class})

            # Create a dictionary with the actions and their permissions
            dict_actions = dict(
                [
                    [x['action_name'],
                    x.get('permission_role', 'can_run_actions')
                ]
                for x in action_list])
            
            # Set diskcache to reduce call on microservice to check for
            # action permission
            default_cache.set(hash_dict=hash_dict, value=dict_actions)

        # Check if the action is available in the dictionary
        if action not in dict_actions.keys():
            msg = (
                "Action [{action}] was is not avaiable at " +
                "model_class[{model_class}]. Call list actions to verify " +
                "the possible actions and its arguments for the model class.")
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
            action: str) -> Dict[str, str]:
        """Map endpoint and HTTP method to Pumpwood role metadata.

        Args:
            route (KongRoute):
                Kong route object.
            method (str):
                HTTP method to map to Pumpwood roles.
            model_class (str):
                Model class parsed from the request path.
            endpoint (str):
                Pumpwood endpoint segment from the path.
            action (str):
                Action name when the endpoint is ``actions``.

        Returns:
            dict:
                Keys ``role``, ``type``, ``model_class``, ``endpoint``,
                and ``action`` describing the resolved permission role.

        Raises:
            PumpWoodNotImplementedError:
                If endpoint or method is not supported.
            PumpWoodActionArgsException:
                If route type or action method is invalid.
            PumpWoodObjectDoesNotExist:
                If a named action is not registered for the model.
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


@dataclass
class PumpwoodAuthHasPermissionCache(PumpwoodDataclassMixin):
    """Cache entry for route permission checks."""

    is_authenticated: bool
    """Whether the request is authenticated."""
    route_id: int
    """Kong route primary key."""
    user_id: int
    """User primary key."""
    role: str
    """Role being validated."""
    action: str
    """Action being validated."""
    context: str = "pumpwood_djangoauth__has_permission"
    """Context for the cache key."""


class RouteAPIPermissionAux:
    """Auxiliary class to check user's permissions for a route."""

    HAS_PERMISSION_CACHE_TAG = "has-permission"
    """Tag used to set cache values for has permission."""

    HAS_PERMISSION_CACHE_TEMPLATE = (
        "has-permission--auth[{is_authenticated}]_r{route_id}_u[{user_id}]_" +
        "r[{role}]_a[{action}]")
    """Template used to create a key for cache."""

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

        # Check for spaces to reduce SQL injection, actions are always python
        # functions they should only be characters, numbers and underlines.
        if ' ' in action:
            msg = (
                'Action [{action}] should not have spaces on name '
                'definition')
            raise PumpWoodForbidden(
                msg, payload={'action': action})

        # Try to retrieve cache from local before retrieving action
        # data from microservice.
        cache_dict = PumpwoodAuthHasPermissionCache(
            is_authenticated=is_authenticated, route_id=route_id,
            user_id=user_id, role=role, action=action)
        cached_value = default_cache.get(cache_dict)
        if cached_value is not None:
            return cached_value

        # Fetch information from user, this information will be used to
        # set the expected permission based on the role
        User = get_user_model()
        user = User.objects.get(id=user_id)

        # If the role is explicity set to super user and user is not
        # return False
        if not user.is_superuser and role == 'is_superuser':
            return False

        # According to the role, set the expected permission based on
        # user information
        has_permission_results = None
        if user.is_superuser:
            has_permission_results = True
        elif role == 'is_authenticated':
            has_permission_results = is_authenticated
        elif role == 'is_staff':
            has_permission_results = user.is_staff
        elif role == 'is_service_user':
            has_permission_results = user.user_profile.is_service_user
        else:
            # If role is not a general role, check if user has permission
            # to the route and action using api permission query
            has_permission_results = cls._get_non_general_roles(
                route_id=route_id, user_id=user.id, role=role,
                action=action)

        # Set cache to reduce call on microservice to check for
        # permission
        default_cache.set(
            cache_dict, has_permission_results,
            expire=TOKEN_CACHE_EXPIRATION)
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
    def from_path(cls, path: str) -> Dict[str, str]:
        """Resolve path components and the matching Kong route.

        Args:
            path (str):
                Request path used for route lookup.

        Returns:
            dict:
                Path components plus ``route`` (``KongRoute`` instance).
                Keys: ``type``, ``model_class``, ``endpoint``, ``action``,
                ``route``.

        Raises:
            PumpWoodObjectDoesNotExist:
                If zero or multiple routes match the path prefix.
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
