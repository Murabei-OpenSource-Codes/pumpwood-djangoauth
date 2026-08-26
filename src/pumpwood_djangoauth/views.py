"""Base Pumpwood Auth REST view mixins for row permission filtering."""
import pandas as pd
from dataclasses import dataclass

from pandas.tseries.frequencies import key
from django.db.models import Q
from pumpwood_communication.cache import default_cache
from pumpwood_communication.type import PumpwoodDataclassMixin
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.config import ROW_PERMISSION_CACHE_EXPIRATION


@dataclass
class PumpWoodAuthUserRowPermissionCache(PumpwoodDataclassMixin):
    """Disk cache entry for a user's row permission identifiers."""

    user_id: str
    """Key to cache the row permission."""
    context: str = 'pumpwood_djangoauth__user_row_permission'
    """Context to cache the row permission."""


class PumpWoodRestServiceRowPermission(PumpWoodRestService):
    """Filter list and retrieve queries using row permission tags.

    Extends ``base_query`` to restrict rows whose ``row_permission_id`` is
    associated with the requesting user through groups or direct links.
    """

    def base_query(self, request, **kwargs):
        """Filter queryset rows by the user's row-permission tags.

        Args:
            request:
                Authenticated Django REST request.
            **kwargs:
                Arguments forwarded to the parent ``base_query``.

        Returns:
            QuerySet | Exception:
                Filtered queryset when the model exposes
                ``row_permission_id``; otherwise an ``Exception`` describing
                unsupported row permissions.
        """
        from pumpwood_djangoauth.registration.models import (
            UserProfile)

        base_query = super().base_query(request, **kwargs)
        has_row_permission_id = hasattr(
            self.service_model, 'row_permission_id')
        if not has_row_permission_id:
            return Exception(
                'Row permission is not supported for this model.')

        # Try to get permissions from local disk cache
        request_user_id = request.user.id
        cache_dict = PumpWoodAuthUserRowPermissionCache(
            user_id=request_user_id)
        row_permission_list = default_cache.get(cache_dict)

        # If not avaiable fetch them from database
        if row_permission_list is None:
            row_permission_list = pd.DataFrame(
                UserProfile.self_row_permissions(request),
                columns=['pk']).loc[:, 'pk'].tolist()

        # Set cache to reduce calls to the database and avoid repeated calls
        # to the database for the same user.
        default_cache.set(
            hash_dict=cache_dict, value=row_permission_list,
            expire=ROW_PERMISSION_CACHE_EXPIRATION)
        return base_query.filter(
            Q(row_permission_id__isnull=True) |
            Q(row_permission_id__in=row_permission_list))

