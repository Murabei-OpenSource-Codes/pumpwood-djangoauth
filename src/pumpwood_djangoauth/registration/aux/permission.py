"""Functions to help fetching permissions from user."""
import pandas as pd
import importlib.resources as pkg_resources
from typing import List
from django.db import connection

# Read sql query from package resources
sql_content = pkg_resources.read_text(
    'pumpwood_djangoauth.registration.aux.query',
    'group_user_permissions.sql')


class PermissionAux:
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
        # Import dependencies on function to skip circular imports
        from pumpwood_djangoauth.system.models import KongRoute
        from pumpwood_djangoauth.system.serializers import KongRouteSerializer

        all_routes = KongRoute.objects.all()
        routed_data = KongRouteSerializer(
            all_routes, many=True, default_fields=True,
            context={'request': request}).data

        list_permissions = []
        for r in routed_data:
            r['__display_name__'] = r.get('route_name')
            list_permissions.append({
                'route_id': r['pk'],
                'route': r,
                'can_list': True,
                'can_list_without_pag': True,
                'can_retrieve': True,
                'can_retrieve_file': True,
                'can_delete': True,
                'can_delete_many': True,
                'can_delete_file': True,
                'can_save': True,
                'can_run_actions': True})
        return list_permissions

    @classmethod
    def _get_non_superuser(cls, user, request) -> List[dict]:
        """Get non superuser permissions associated with user."""
        from pumpwood_djangoauth.system.models import KongRoute
        from pumpwood_djangoauth.system.serializers import KongRouteSerializer

        query_parameters = {"user_id": user.id}
        with connection.cursor() as cursor:
            cursor.execute(sql_content, query_parameters)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        pd_results = pd.DataFrame(rows, columns=columns)

        query_result = KongRoute.objects.filter(id__in=pd_results['route_id'])
        routed_data = KongRouteSerializer(
            query_result, many=True, default_fields=True,
            context={'request': request}).data
        for r in routed_data:
            r['__display_name__'] = r.get('route_name')
        map_route = dict([(r['pk'], r) for r in routed_data])

        pd_results['route'] = pd_results['route_id'].map(map_route)
        return pd_results
