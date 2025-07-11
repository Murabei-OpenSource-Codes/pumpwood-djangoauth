"""Module to implement custom permission for Pumpwod End-Points."""
from typing import Union, List
from rest_framework.permissions import IsAuthenticated
from pumpwood_djangoauth.system.models import KongRoute
from pumpwood_djangoauth.config import (
    diskcache, DISKCACHE_EXPIRATION, microservice)
from pumpwood_communication.exceptions import (
    PumpWoodOtherException, PumpWoodException, PumpWoodObjectDoesNotExist)


class PumpwoodPermission(IsAuthenticated):
    """Use api permission to check if user can perform action."""

    API_PERMISSION_CACHE_TAG = 'api-permission'
    """Tag to organize api permission disk cache."""
    ACTION_PERMISSION_CACHE_TAG = 'action-permission'
    """Tag to organize action permission disk cache."""

    def has_permission(self, request, view) -> bool:
        """Implement has_permission function to check at api permission.

        Args:
            request:
                Django request.
            view:
                Django view.

        Returns:
            Return True if user has access to the resource.
        """
        # Check first if user is IsAuthenticated
        super_has_permission = super().has_permission(request, view)
        if not super_has_permission:
            return super_has_permission
        return True
        return KongRoute.self_has_permission(
            request=request, path=request.path, method=request.method)

        model_class, endpoint, action = self._get_endpoint(path=request.path)
        print("endpoint, action:", endpoint, action)
        route_begin_path = self._get_routing_path(path=request.path)
        role = None
        if endpoint == 'actions':
            # Check if call is to execute an action, if not it is
            # informational get action, permit for all users that are
            # IsAuthenticated
            if action:
                action_permission = self._get_action_permission(
                    model_class=model_class, action=action)
                if action_permission == 'default':
                    role = KongRoute.map_request_to_role(
                        endpoint=endpoint, method=request.method)
            else:
                role = 'authenticated'
        else:
            role = KongRoute.map_request_to_role(
                endpoint=endpoint, method=request.method)

        # Try to get permission from cache before fetching from database
        permission_cache = self._get_permission_cache(
            endpoint=endpoint, route_begin_path=route_begin_path,
            user_id=request.user.id)
        if permission_cache is not None:
            return permission_cache
        else:
            route = self._get_route(route_begin_path=route_begin_path)
            is_permission_ok = route.self_has_role(request=request, role=role)
            # Set local disk cache to reduce database calls
            self._set_permission_cache(
                endpoint=endpoint, route_begin_path=route_begin_path,
                user_id=request.user.id, has_permission=is_permission_ok)
            return is_permission_ok

    @classmethod
    def _get_action_permission(cls, model_class: str,
                               action: str) -> List[str]:
        """Fetch action information and check if permission is set.

        Args:
            model_class (str):
                Model class associated with permission.
            action (str):
                Name of the action that is beening checked for permission.

        Returns:
            Return permission associated with action.
        """
        # Try to fetch action permission role from cache before requesting
        # information at the API
        action_role = cls._get_action_permission_cache(
            model_class=model_class, action=action)
        if action_role is not None:
            return action_role

        # Fetch model class action info from endpoint
        try:
            list_actions_results = microservice\
                .list_actions(model_class=model_class)
            actions_role_map = dict([
                [x['action_name'], x.get('permission_role')]
                for x in list_actions_results])
        except PumpWoodException as e:
            raise e

        action_role = actions_role_map.get(action)
        if action_role is None:
            msg = (
                "Action [{action}] not found on model class [{model_class}]." +
                " Possible actions:\n {action_list}")\
                .format(
                    action=action, model_class=model_class,
                    action_list=list(actions_role_map.keys()))
            raise PumpWoodObjectDoesNotExist(message=msg)

        cls._set_action_permission_cache(
            model_class=model_class, action=action, action_role=action_role)
        return action_role

    @classmethod
    def _get_action_permission_cache_key(cls, model_class: str,
                                         action: str) -> str:
        """Create key to be used on permission cache.

        Args:
            model_class (str):
                Model class of the action.
            action (str):
                Action associated to check the permission policy.

        Returns:
            The key value used to access the cache.
        """
        key = "action-permission__m[{model_class}]__a[{action}]"\
            .format(model_class=model_class, action=action)
        return key

    @classmethod
    def _get_action_permission_cache(cls, model_class: str,
                                     action: str) -> str:
        """Get actions permission permission role from diskcache.

        Args:
            model_class (str):
                Model class of the action.
            action (str):
                Action associated to check the permission policy.

        Returns:
            The key value used to access the cache.
        """
        key = cls._get_action_permission_cache_key(
            model_class=model_class, action=action)
        return diskcache.get(key)

    @classmethod
    def _set_action_permission_cache(cls, model_class: str,
                                     action: str, action_role: str) -> str:
        """Get actions permission permission role from diskcache.

        Args:
            model_class (str):
                Model class of the action.
            action (str):
                Action associated to check the permission policy.
            action_role (str):
                Role to be set on action permission role cache.

        Returns:
            The key value used to access the cache.
        """
        key = cls._get_action_permission_cache_key(
            endpoint=model_class, route_begin_path=action)
        return diskcache.set(
            key=key, value=action_role, expire=DISKCACHE_EXPIRATION,
            tag=cls.ACTION_PERMISSION_CACHE_TAG)

    @classmethod
    def _get_permission_cache_key(cls, endpoint: str, route_begin_path: str,
                                  user_id: int) -> str:
        """Create key to be used on permission cache.

        Args:
            endpoint (str):
                Endpoint associated with permission.
            route_begin_path (str):
                Route path begin used on kong reverse proxy redirecting.
            user_id (int):
                ID of the user associated with cache.

        Returns:
            The key value used to access the cache.
        """
        key = (
            "api-permission__e[{endpoint}]__r[{route_begin_path}]__" +
            "u[{user_id}]").format(
                endpoint=endpoint, route_begin_path=route_begin_path,
                user_id=user_id)
        return key

    @classmethod
    def _get_permission_cache(cls, endpoint: str, route_begin_path: str,
                              user_id: int) -> Union[bool, None]:
        """Get permission from disk cache according to parameters.

        Args:
            endpoint (str):
                Endpoint associated with permission.
            route_begin_path (str):
                Route path begin used on kong reverse proxy redirecting.
            user_id (int):
                ID of the user associated with cache.

        Returns:
            The key value used to access the cache.
        """
        key = cls._get_permission_cache_key(
            endpoint=endpoint, route_begin_path=route_begin_path,
            user_id=user_id)
        return diskcache.get(key)

    @classmethod
    def _set_permission_cache(cls, endpoint: str, route_begin_path: str,
                              user_id: int, has_permission: bool) -> bool:
        """Set permission at disk cache according to parameters.

        Args:
            endpoint (str):
                Endpoint associated with permission.
            route_begin_path (str):
                Route path begin used on kong reverse proxy redirecting.
            user_id (int):
                ID of the user associated with cache.
            has_permission (bool):
                Value to set as cache.

        Returns:
            Return True if value was set as cache.
        """
        key = cls._get_permission_cache_key(
            endpoint=endpoint, route_begin_path=route_begin_path,
            user_id=user_id)
        return diskcache.set(
            key=key, value=has_permission, expire=DISKCACHE_EXPIRATION,
            tag=cls.API_PERMISSION_CACHE_TAG)

    def _get_routing_path(self, path: str) -> bool:
        """Extract the initial path used on kong routing of Pumpwood Views.

        Pumpwood views are build in order to respect the path template
        `/rest/{model class}/{endpoint}/` the first two subpaths are used
        by Kong to route the calls to the correct microservice.

        This function will extract this firt part of the path to use on
        caching and query route id on database.
        """
        path_segments = path.split('/')
        route_begin_path = "/".join(path_segments[:3]) + "/"
        return route_begin_path

    def _get_route(self, route_begin_path: str) -> KongRoute:
        """Get route object using the begin path to query database.

        Args:
            route_begin_path (str):
                Begining of the path that is used to redirect calls at
                `KongRoute`.

        Returns:
            Return a KongRoute object correponding to begin path used to
            redirect calls to microservice.
        """
        query_parameter = {
            'path_begin': route_begin_path}
        route_results = list(
            KongRoute.objects.raw(_permission_query, query_parameter))
        if len(route_results) == 0:
            return None
        elif len(route_results) == 1:
            return route_results[0]
        else:
            msg_text_list = []
            for r in route_results:
                msg_part = (
                    "id[{id}] route_name[{route_name}] " +
                    "route_url[{route_url}]")\
                    .format(id=r.id, route_url=r.route_url,
                            route_name=r.route_name)
                msg_text_list.append(msg_part)
            msg = (
                "Something is wrong at route register, there is two or more"
                " routes with same route begining:\n{routes}")\
                .format(routes="\n".join(msg_text_list))
            raise PumpWoodOtherException(message=msg)

    def _get_endpoint(self, path: str):
        """Get endpoint from path."""
        path_segments = path.split('/')
        if len(path_segments) < 4:
            return '## custom ##'
        else:
            print("path_segments:", path_segments)
            endpoint = path_segments[3]
            action = None
            if endpoint == 'actions':
                action = path_segments[4]
            return path_segments[2], path_segments[3], action
