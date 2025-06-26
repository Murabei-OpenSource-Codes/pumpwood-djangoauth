"""Functions to help fetching permissions from user."""
import pandas as pd
from typing import List


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

        return [
            'tem que implementar'
        ]

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
                'description': '## superuser ##',
                'notes': '## superuser ##',
                'route': r,
                'dimensions': {},
                'can_list': 'allow',
                'can_list_without_pag': 'allow',
                'can_retrieve': 'allow',
                'can_retrieve_file': 'allow',
                'can_delete': 'allow',
                'can_delete_many': 'allow',
                'can_delete_file': 'allow',
                'can_save': 'allow',
                'can_run_actions': 'allow',
                'extra_info': {},
                'updated_by': None,
                'updated_at': None})
        return list_permissions

    @classmethod
    def _get_non_superuser(cls, user, request) -> List[dict]:
        """Get non superuser permissions associated with user."""
        from pumpwood_djangoauth.api_permission.models import (
            PumpwoodPermissionPolicy)
        from pumpwood_djangoauth.api_permission.serializers import (
            SerializerPumpwoodPermissionPolicy)
        columns = [
            'custom_policy_id', 'priority', 'general_policy',
            'custom_policy__route_id']
        pd_users_policies = pd.DataFrame(
            user.api_permission_set.all().values(*columns),
            columns=columns)

        columns = [
            'group__api_permission_set__custom_policy_id',
            'group__api_permission_set__priority',
            'group__api_permission_set__general_policy',
            'group__api_permission_set__custom_policy__route_id']
        pd_group_policies = pd.DataFrame(
            user.user_group_m2m_set.all().values(*columns),
            columns=columns)\
            .rename(columns={
                'group__api_permission_set__custom_policy_id':
                    'custom_policy_id',
                'group__api_permission_set__priority':
                    'priority',
                'group__api_permission_set__general_policy':
                    'general_policy',
                'group__api_permission_set__custom_policy__route_id':
                    'custom_policy__route_id'})

        all_policies = pd.concat([pd_users_policies, pd_group_policies])
        permission_objects = PumpwoodPermissionPolicy.objects.filter(
            id__in=all_policies['custom_policy_id'])
        all_policies_data = pd.DataFrame(SerializerPumpwoodPermissionPolicy(
            permission_objects, many=True, related_fields=True,
            context={'request': request}).data)
        all_policies_data
