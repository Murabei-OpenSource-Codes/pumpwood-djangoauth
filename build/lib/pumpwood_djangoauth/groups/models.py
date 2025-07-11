"""
Django models to set custom groups permission for Pumpwood end-points.

.. warning::
    End-points not functional yet.
"""
from django.db import models
from django.conf import settings
from pumpwood_communication.serializers import PumpWoodJSONEncoder


class PumpwoodUserGroup(models.Model):
    """Permission group for Pumpwood End-Points.

    Create permission groups associating many users in a group to apply
    PermissionPolicy collectivity.

    Model fields:
        - **description [TextField]:** Description of the permission group.
        - **notes [TextField]:** Long notes associated with permission group.
        - **dimensions [JSONField]:** Key/Value tags for organization of
            permission groups on database.
        - **extra_info [JSONField]:** Extra information that can be helpfull
            on the future.
        - **updated_by [ForeignKey('User')]:** Foreign key associated with
            User model class of the user resposible for creation and update.
        - **updated_at [DateTimeField]:** Date/Time when the permission
            group was updated.
    """

    description = models.TextField(
        null=False, unique=True, blank=False,
        verbose_name="Description",
        help_text="A short description of the route.")
    """@private"""
    notes = models.TextField(
        null=False, default="", blank=True,
        verbose_name="Notes",
        help_text="A long description of the route.")
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
        related_name='pumpwood_user_group_set',
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
        return self.description

    class Meta:
        """Meta class."""
        db_table = 'groups__group'
        verbose_name = 'Permission Group'
        verbose_name_plural = 'Permission Groups'


class PumpwoodUserGroupM2M(models.Model):
    """Permission group user association.

    M2M model class to associate users with groups.

    Model fields:
        - **user [ForeignKey('User')]:**
            Foreign Key from User model class to associate with
            PumpwoodPermissionGroup.
        - **group [ForeignKey('PumpwoodPermissionGroup')]:**
            Foreign Key from PumpwoodPermissionGroup model class.
        - **extra_info [JSONField]:**
            Extra information associated with relation between User and
            PumpwoodPermissionGroup.
        - **updated_by [ForeignKey]:** Foreign Key associated with user
            repossible for updating and creating relation between User and
            PumpwoodPermissionGroup.
        - **updated_at [DateTimeField]:** Date/time the relation between User
            and PumpwoodPermissionGroup was created or updated.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="user_group_m2m_set", verbose_name="User",
        help_text="User associated with group")
    """@private"""
    group = models.ForeignKey(
        PumpwoodUserGroup, on_delete=models.CASCADE,
        related_name="user_group_m2m_set", verbose_name="Group",
        help_text="Permission Group to apply policy")
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
        related_name='pumpwood_user_group_m2m_updated_by_set',
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
        db_table = 'groups__group_user_m2m'
        unique_together = [['user', 'group', ], ]
        verbose_name = 'User -> Group'
        verbose_name_plural = 'User -> Group'
