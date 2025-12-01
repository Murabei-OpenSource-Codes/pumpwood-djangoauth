"""Module for models to row permission on Pumpwood.

Different from API permission, row permission will define if the user can
see and edit information on the database, it by default will be applied (or
used to be applied) on all retrieve, list and aggregate end-points using
base_query function.
"""
from django.db import models
from django.conf import settings
from pumpwood_communication.serializers import PumpWoodJSONEncoder

# User groups
from pumpwood_djangoauth.groups.models import PumpwoodUserGroup


class PumpwoodRowPermission(models.Model):
    """Tag associated with row permission.

    It is used to indicate if a user can retrieve or edit an inforamtion.
    """
    description = models.TextField(
        null=False, unique=True, blank=False,
        verbose_name="Description",
        help_text="A short description of permission.")
    """@private"""
    notes = models.TextField(
        null=False, default="", blank=True,
        verbose_name="Notes",
        help_text="A long description of permission.")
    """@private"""
    dimensions = models.JSONField(
        default=dict, blank=True,
        verbose_name="Dimentions",
        help_text="Dictionary of tags to help organization",
        encoder=PumpWoodJSONEncoder)
    """@private"""
    extra_info = models.JSONField(
        default=dict, blank=True,
        verbose_name="Extra info.",
        help_text="Other information that can be usefull",
        encoder=PumpWoodJSONEncoder)
    """@private"""
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True,
        related_name='row_permission_tag_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """@private"""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """@private"""

    def __str__(self):
        """__str__."""
        return f"{self.id} || {self.description}"

    class Meta:
        """Meta class."""
        db_table = 'row_permission__description'
        verbose_name = 'Row permission'
        verbose_name_plural = 'Row permissions'


class PumpwoodRowPermissionGroupM2M(models.Model):
    """Link PumpwoodRowPermission and PumpwoodRowPermissionGroup.

    Associate row permission policies with groups to apply it to all users
    that belongs to the group.

    Model fields:
        - **group [ForeignKey('PumpwoodRowPermissionGroup')]:**
            Foreign Key to associated policy with group.
        - **row_permission [PumpwoodRowPermission]:**
            Row policy associate with group, it will affect all Pumpwood
            end-points.
        - **extra_info [JSONField]:**
            Extra information that might be important.
        - **updated_by [ForeignKey]:**
            User that created/updated the relation between
            PumpwoodRowPermissionGroup and policies
        - **updated_at [DateTimeField]:**
            Date/time the relation was created/updated.
    """
    group = models.ForeignKey(
        PumpwoodUserGroup, on_delete=models.CASCADE,
        related_name="row_permission_set", verbose_name="Group",
        help_text="User Group to apply policy")
    """@private"""
    row_permission = models.ForeignKey(
        PumpwoodRowPermission, on_delete=models.CASCADE,
        related_name="group_set", verbose_name="Group",
        help_text="Row permission Group to apply policy")
    """@private"""
    extra_info = models.JSONField(
        default=dict, blank=True,
        verbose_name="Extra info",
        help_text="Other information that can be usefull",
        encoder=PumpWoodJSONEncoder)
    """@private"""
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True,
        related_name='row_permission_group_updated_by_m2m_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """@private"""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """@private"""

    class Meta:
        """Meta class."""
        db_table = 'row_permission__group_m2m'
        verbose_name = 'Row permission Policy -> Group'
        verbose_name_plural = 'Row permission Policy -> Group'


class PumpwoodRowPermissionUserM2M(models.Model):
    """Link PermissionPolicy and User.

    Associate permission policies with users individualy.

    Model class:
        - **priority [IntegerField]:**
            Integer setting priority to permission policy. Lower numbers with
            have priority.
        - **user [ForeignKey('user')]:**
            Foreign Key to associated policy with user.
        - **row_permission [PumpwoodRowPermission]:**
            Row policy associate with group, it will affect all Pumpwood
            end-points.
        - **extra_info [JSONField]:**
            Extra information that might be important.
        - **updated_by [ForeignKey]:**
            User that created/updated the relation between
            PumpwoodPermissionGroup and policies
        - **updated_at [DateTimeField]:**
            Date/time the relation was created/ updated.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="row_permission_set",
        verbose_name="User",
        help_text="Row Permission user to apply policy")
    """@private"""
    row_permission = models.ForeignKey(
        PumpwoodRowPermission, on_delete=models.CASCADE,
        null=True, blank=True, related_name="user_set",
        verbose_name="Row Policy",
        help_text="Row policy that will be applied to the group")
    """@private"""
    extra_info = models.JSONField(
        default=dict, blank=True,
        verbose_name="Extra info.",
        help_text="Other information that can be usefull",
        encoder=PumpWoodJSONEncoder)
    """@private"""
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True,
        related_name='row_permission_user_updated_by_m2m_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """@private"""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """@private"""

    class Meta:
        """Meta class."""
        db_table = 'row_permission__user_m2m'
        verbose_name = 'Row permission Policy -> User'
        verbose_name_plural = 'Row permission Policy -> User'
