"""Module for models to row permission on Pumpwood.

Different from API permission, row permission will define if the user can
see and edit information on the database, it by default will be applied (or
used to be applied) on all retrieve, list and aggregate end-points using
base_query function.
"""
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from pumpwood_communication.serializers import PumpWoodJSONEncoder

# User groups
from pumpwood_djangoauth.groups.models import PumpwoodUserGroup


class PumpwoodRowPermissionTag(models.Model):
    """Tag associated with row permission.

    It is used to indicate if a user can retrieve or edit an inforamtion.
    """
    description = models.TextField(
        null=False, unique=True, blank=False,
        verbose_name="Description",
        help_text="A short description of the tag.")
    """@private"""
    notes = models.TextField(
        null=False, default="", blank=True,
        verbose_name="Notes",
        help_text="A long description of the tag.")
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

    class Meta:
        """Meta class."""
        db_table = 'row_permission__tag'
        verbose_name = 'Row permission tag'
        verbose_name_plural = 'Row permission tags'


class PumpwoodRowPermissionPolicy(models.Model):
    """Row Permission Policy to be applied at tag.

    Create a permission for a tag if it is possible to retrieve, update or
    delete inforamtion.

    .. warning::
        End-points not functional yet.

    Model fields:
        - **notes [TextField]:**
            Long descriptions for PumpwoodRowPermissionPolicy objects.
        - **dimensions [JSONField]:**
            Key/Value dictionary with information to help organization/fetch
            of the data.
        - **tag [ForeignKey('PumpwoodRowPermissionTag')]:**
            ForeignKey to PumpwoodRowPermissionTag model_class. It corresponds
            to the route at which the permission policy will be applied.
        - **can_retrieve [choices]:**
            If policy permits user to retrieve data from row market by
            tag.
        - **can_update [choices]:**
            If policy permits user to retrieve data from row market by
            tag.
        - **can_delete [choices]:**
            If policy permits user to retrieve data from row market by
            tag.
        - **extra_info [JSONField]:** Dictionary with extra information
            that might be usefull.
        - **updated_by [ForeignKey('User')]:** Foreign Key to the user
            repossible for updating the policy.
        - **updated_at [models.DateTimeField]:** Date/time the policy was
            created/updated.
    """

    PERMISSION_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
        ('no_change', 'No change'),
    ]
    """Permission choices that will restrict can_retrieve, can_update,
    can_delete."""

    description = models.TextField(
        null=False, unique=True, blank=False,
        verbose_name="Description",
        help_text="A short description of the row permission policy.")
    """@private"""
    notes = models.TextField(
        null=False, default="", blank=True,
        verbose_name="Notes",
        help_text="A long description of the row permission policy.")
    """@private"""
    dimensions = models.JSONField(
        default=dict, blank=True,
        verbose_name="Dimentions",
        help_text="Dictionary of tags to help organization",
        encoder=PumpWoodJSONEncoder)
    """@private"""
    can_retrieve = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Can retrieve?",
        help_text="Permission to retrive row data")
    """@private"""
    can_update = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Can update?",
        help_text="Permission to update row data")
    """@private"""
    can_delete = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Can Delete?",
        help_text="Permission to delete row")
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
        related_name='row_permission_policy_set',
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
        db_table = 'row_permission__policy'
        verbose_name = 'Row Permission Policy'
        verbose_name_plural = 'Row Permission Policies'


class PumpwoodRowPermissionPolicyGroupM2M(models.Model):
    """Link PumpwoodRowPermissionPolicy and PumpwoodRowPermissionGroup.

    Associate row permission policies with groups to apply it to all users
    that belongs to the group.

    Model fields:
        - **priority [IntegerField]:**
            Integer setting priority to permission policy. Lower numbers with
            have priority.
        - **group [ForeignKey('PumpwoodRowPermissionGroup')]:**
            Foreign Key to associated policy with group.
        - **policy [PumpwoodRowPermissionPolicy]:**
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

    priority = models.IntegerField(
        null=False, default=0, verbose_name="Policy priority",
        help_text="Policy priority, lower number will have precedence")
    """@private"""
    group = models.ForeignKey(
        PumpwoodUserGroup, on_delete=models.CASCADE,
        related_name="row_permission_set", verbose_name="Group",
        help_text="User Group to apply policy")
    """@private"""
    policy = models.ForeignKey(
        PumpwoodRowPermissionPolicy, on_delete=models.CASCADE,
        related_name="permission_set", verbose_name="Group",
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
        db_table = 'row_permission__policy_group_m2m'
        verbose_name = 'Row permission Policy -> Group'
        verbose_name_plural = 'Row permission Policy -> Group'


class PumpwoodPermissionPolicyUserM2M(models.Model):
    """Link PermissionPolicy and User.

    Associate permission policies with users individualy.

    Model class:
        - **priority [IntegerField]:**
            Integer setting priority to permission policy. Lower numbers with
            have priority.
        - **user [ForeignKey('user')]:**
            Foreign Key to associated policy with user.
        - **general_policy [TextField]:**
            General policy associate with group, it will affect all Pumpwood
            end-points.
        - **custom_policy [ForeignKey]:**
            Foreign Key to associate a PumpwoodPermissionPolicy to a
            PumpwoodPermissionGroup.
        - **extra_info [JSONField]:**
            Extra information that might be important.
        - **updated_by [ForeignKey]:**
            User that created/updated the relation between
            PumpwoodPermissionGroup and policies
        - **updated_at [DateTimeField]:**
            Date/time the relation was created/ updated.
    """

    priority = models.IntegerField(
        null=False, default=0, verbose_name="Policy priority",
        help_text="Policy priority, lower number will have precedence")
    """@private"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="row_permission_set",
        verbose_name="User",
        help_text="Row Permission user to apply policy")
    """@private"""
    policy = models.ForeignKey(
        PumpwoodRowPermissionPolicyGroupM2M, on_delete=models.CASCADE,
        null=True, blank=True, related_name="policy_user_set",
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
        db_table = 'row_permission__policy_user_m2m'
        verbose_name = 'Row permission Policy -> User'
        verbose_name_plural = 'Row permission Policy -> User'
