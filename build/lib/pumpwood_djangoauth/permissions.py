"""Module to implement custom permission for Pumpwod End-Points."""
from typing import Union, List
from rest_framework.permissions import IsAuthenticated
from pumpwood_djangoauth.system.models import KongRoute
from pumpwood_djangoauth.config import (
    diskcache, DISKCACHE_EXPIRATION, microservice)


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
        has_permission_result = KongRoute.self_has_permission(
            request=request, path=request.path,
            method=request.method)
        print("has_permission_result:", has_permission_result)
        return has_permission_result['has_permission']
