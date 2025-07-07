"""Module to implement custom permission for Pumpwod End-Points."""
from typing import Union
from rest_framework.permissions import BasePermission
from pumpwood_djangoauth.system.models import KongRoute
from pumpwood_djangoauth.config import diskcache, DISKCACHE_EXPIRATION
from pumpwood_communication.exceptions import PumpWoodOtherException


_permission_query = """
SELECT *
FROM public.pumpwood__route
WHERE starts_with(%(path_begin)s, route_url)
"""


class PumpwoodPermission(BasePermission):
    """Use api permission to check if user can perform action."""

    API_PERMISSION_CACHE_TAG = 'api-permission'
    """Tag to organize permission cache."""

    def has_permission(self, request, view):
        """Implemente has_permission function to check at api permission.

        Args:
            request:
                Django request.
            view:
                Django view.
        """
        endpoint = self._get_endpoint(path=request.path)
        route_begin_path = self._get_routing_path(path=request.path)
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
            "e[{endpoint}]__r[{route_begin_path}]__" +
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
            return path_segments[3]
