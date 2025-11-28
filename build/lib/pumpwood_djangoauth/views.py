"""Super default pumpwood views to add new features."""
import pandas as pd
from typing import List, Union
from django.db.models import Q
from pumpwood_djangoauth.config import diskcache, DISKCACHE_EXPIRATION
from pumpwood_djangoviews.views import (
    PumpWoodRestService, PumpWoodDataBaseRestService)


class PumpWoodRestServiceRowPermission(PumpWoodRestService):
    """Super PumpWoodRestService to filter implement row base filter.

    Super base_query to filter object with `row_permission_id` that are
    associated with user by group or directly to it
    """

    ROW_PERMISSION_CACHE_TAG = 'row_permission'

    @classmethod
    def get_row_permission_cache_key(cls, user_id: int) -> str:
        """Return user's row permission cache key."""
        template = "row-permission--{user_id}"
        return template.format(user_id=user_id)

    @classmethod
    def get_row_permission_cache(cls, user_id: int) -> Union[List[int], None]:
        """Get user's row_permission from cache.

        Get user row_permissions from disk cache reducing
        processing time.

        Args:
            user_id (int):
                User primary key.

        Returns:
            Return a list with row_permission associated with user or None
            if values are not at cache.
        """
        key = cls.get_row_permission_cache_key(user_id=user_id)
        return diskcache.get(key)

    @classmethod
    def set_row_permission_cache(cls, user_id: int,
                                 row_permissions: List[int]) -> bool:
        """Set user's row_permission from cache.

        Set user row_permissions cache using `config.DISKCACHE_EXPIRATION`
        as expire argument and `cls.ROW_PERMISSION_CACHE_TAG` as tag.

        Args:
            user_id (int):
                User primary key.
            row_permissions (List[int]):
                Ids of the row permissions associated with user.

        Returns:
            Return a boolean value if the row_permission is set at .
        """
        key = cls.get_row_permission_cache_key(user_id=user_id)
        return diskcache.set(
            key=key, value=row_permissions, expire=DISKCACHE_EXPIRATION,
            tag=cls.ROW_PERMISSION_CACHE_TAG)

    def base_query(self, request, **kwargs):
        """Super base query to filter using row_permission_id if present."""
        from pumpwood_djangoauth.registration.models import (
            UserProfile)

        base_query = super().base_query(request, **kwargs)
        has_row_permission_id = hasattr(
            self.service_model, 'row_permission_id')
        if not has_row_permission_id:
            return base_query

        # Try to get permissions from local disk cache
        row_permission_list = (
            self.get_row_permission_cache(user_id=request.user.id))

        # If not avaiable fetch them from database
        if row_permission_list is None:
            row_permission_list = pd.DataFrame(
                UserProfile.self_row_permissions(request),
                columns=['pk']).loc[:, 'pk'].tolist()
            self.set_row_permission_cache(
                user_id=request.user.id,
                row_permissions=row_permission_list)

        return base_query.filter(
            Q(row_permission_id__isnull=True) |
            Q(row_permission_id__in=row_permission_list))


class PumpWoodDBRestServiceRowPermission(PumpWoodDataBaseRestService,
                                         PumpWoodRestServiceRowPermission):
    """Super PumpWoodDataBaseRestService to add row_permission filter."""
    pass
