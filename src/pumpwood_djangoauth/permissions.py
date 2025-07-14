"""Module to implement custom permission for Pumpwod End-Points."""
from rest_framework.permissions import IsAuthenticated
from pumpwood_communication.exceptions import (
    PumpWoodUnauthorized, PumpWoodForbidden)
from pumpwood_djangoauth.system.models import KongRoute


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
            request=request, path=request.path, method=request.method)
        is_unauthorized = (
            not request.user.is_authenticated and
            not has_permission_result['has_permission'])
        if is_unauthorized:
            msg = ("Your credentials are not valid.")
            raise PumpWoodUnauthorized(msg)

        if not has_permission_result['has_permission']:
            msg = (
                "You have valid credentials, but do not have permission"
                "to perform this action. Endpoint information:\n"
                "- model_class: {model_class}\n"
                "- endpoint: {endpoint}\n"
                "- action: {action}"
                "- expected role: {role}")
            raise PumpWoodForbidden(
                msg, payload={
                    "model_class": has_permission_result["model_class"],
                    "endpoint": has_permission_result["endpoint"],
                    "action": has_permission_result["action"],
                    "role": has_permission_result["role"]})
        return has_permission_result['has_permission']

    def get_has_permission_cache(self, request, view) -> bool:
        """
        """
