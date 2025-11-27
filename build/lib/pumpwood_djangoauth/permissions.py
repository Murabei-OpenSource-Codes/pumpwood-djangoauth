"""Module to implement custom permission for Pumpwod End-Points."""
from rest_framework.permissions import IsAuthenticated
from pumpwood_communication.exceptions import (
    PumpWoodUnauthorized, PumpWoodForbidden)
from pumpwood_djangoauth.system.models import KongRoute


class PumpwoodPermission(IsAuthenticated):
    """Use api permission to check if user can perform action."""

    role: str = None
    """If will overwrite the expected role at the endpoint according
       to path."""

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
            request=request, path=request.path, method=request.method,
            role=self.role)
        is_authenticated = (
            not request.user.is_authenticated and
            not has_permission_result['has_permission'])
        if is_authenticated:
            msg = ("Your credentials are not valid.")
            raise PumpWoodUnauthorized(msg)

        if not has_permission_result['has_permission']:
            msg = (
                "You have valid credentials, but do not have permission " +
                "to perform this action. Endpoint information:\n" +
                "- model_class: {model_class}\n" +
                "- endpoint: {endpoint}\n" +
                "- action: {action}" +
                "- expected role: {role}")
            raise PumpWoodForbidden(
                msg, payload={
                    "model_class": has_permission_result["model_class"],
                    "endpoint": has_permission_result["endpoint"],
                    "action": has_permission_result["action"],
                    "role": has_permission_result["role"]})
        return has_permission_result['has_permission']


class PumpwoodAllowAny(PumpwoodPermission):
    """Overwrite expected role at end-point to `allow_any`."""

    role = 'allow_any'


class PumpwoodIsAuthenticated(PumpwoodPermission):
    """Overwrite expected role at end-point to `is_authenticated`."""

    role = 'is_authenticated'


class PumpwoodIsStaff(PumpwoodPermission):
    """Overwrite expected role at end-point to `is_staff`."""

    role = 'is_staff'


class PumpwoodCanDelete(PumpwoodPermission):
    """Overwrite expected role at end-point to `can_delete`."""

    role = 'can_delete'


class PumpwoodCanDeleteFile(PumpwoodPermission):
    """Overwrite expected role at end-point to `can_delete_file`."""

    role = 'can_delete_file'


class PumpwoodCanDeleteMany(PumpwoodPermission):
    """Overwrite expected role at end-point to `can_delete_many`."""

    role = 'can_delete_many'


class PumpwoodCanList(PumpwoodPermission):
    """Overwrite expected role at end-point to `can_list`."""

    role = 'can_list'


class PumpwoodCanListWithoutPag(PumpwoodPermission):
    """Overwrite expected role at end-point to `can_list_without_pag`."""

    role = 'can_list_without_pag'


class PumpwoodCanRetrieve(PumpwoodPermission):
    """Overwrite expected role at end-point to `can_retrieve`."""

    role = 'can_retrieve'


class PumpwoodCanRetrieveFile(PumpwoodPermission):
    """Overwrite expected role at end-point to `can_retrieve_file`."""

    role = 'can_retrieve_file'


class PumpwoodCanRunActions(PumpwoodPermission):
    """Overwrite expected role at end-point to `can_run_actions`."""

    role = 'can_run_actions'


class PumpwoodCanSave(PumpwoodPermission):
    """Overwrite expected role at end-point to `can_save`."""

    role = 'can_save'
