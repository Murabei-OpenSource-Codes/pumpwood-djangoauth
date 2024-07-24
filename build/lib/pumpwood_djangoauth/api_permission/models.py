"""
Django models to set custom permission for Pumpwood end-points.

.. warning::
    End-points not functional yet.
"""
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from pumpwood_communication.serializers import PumpWoodJSONEncoder
from pumpwood_communication import exceptions


class PumpwoodPermissionPolicy(models.Model):
    """
    Permission Policy to be applied at Pumpwood End-points.

    Permission policy is a set of diffent permission associated with and
    an end-point. Permission Policy can be associated with Users or Groups
    with a priority parameter.

    .. warning::
        End-points not functional yet.

    Model fields:
        - **description [models.TextField]:**
            Unique description for PumpwoodPermissionPolicy objects.
        - **notes [models.TextField]:** Long descriptions for
            PumpwoodPermissionPolicy objects.
    """

    PERMISSION_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
        ('no_change', 'No change'),
    ]
    """Permission choices that will restrict `can_list, can_list_without_pag,
       can_retrieve, can_retrieve_file, can_delete, can_delete_many,
       can_delete_file, can_save, can_run_actions` attributes."""

    ACTION_PERMISSION_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
        ('custom', 'Custom'),
        ('no_change', 'No change'),
    ]
    """Action Permission choices that will restrict `can_run_actions`
       attribute."""

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
    """Key/Value tags to help organization."""
    route = models.ForeignKey(
        'system.KongRoute', on_delete=models.CASCADE,
        related_name="permission_set", verbose_name="Route",
        help_text="Route associated with permission.")
    """Foreign Key for KongRoute associated with permissions."""
    can_list = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="List",
        help_text="Permission to list end-point and front-end page")
    """Permission associated with list end-points."""
    can_list_without_pag = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="List Without Pag.",
        help_text=(
            "Permission to list without pagination end-point. Return all "
            "values associated with query (list paginate 50)"))
    """Permission associated with list without pag end-point."""
    can_retrieve = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Retrieve",
        help_text="Permission to retrieve end-point and front-end page")
    """Permission associated with retrieve end-point."""
    can_retrieve_file = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Retrieve File",
        help_text="Permission to retrieve file end-point")
    """Permission associated with retrieve file end-point."""
    can_delete = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Delete",
        help_text="Permission to delete object end-point and front-end page")
    """Permission associated with delete end-point."""
    can_delete_many = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Delete Many",
        help_text="Permission to delete many end-point")
    """Permission associated with delete many end-point."""
    can_delete_file = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Delete File",
        help_text="Permission to delelte file end-point")
    """Permission associated with delete file end-point."""
    can_save = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Save",
        help_text="Permission to save end-point and front-end page")
    """Permission associated with save end-point."""
    can_run_actions = models.TextField(
        choices=ACTION_PERMISSION_CHOICES,
        default="no_change", verbose_name="Actions",
        help_text="Permission to run actions")
    """Permission associated with execute action end-point."""
    extra_info = models.JSONField(
        default=dict, blank=True,
        verbose_name="Extra info.",
        help_text="Other information that can be usefull",
        encoder=PumpWoodJSONEncoder)
    """Extra-info associated with permission object."""
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True,
        related_name='policy_updated_by_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """User that updated/created object."""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """When the object was modified."""

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'api_permission__policy'
        verbose_name = 'Permission Policy'
        verbose_name_plural = 'Permission Policies'

    @classmethod
    def list_user_permissions(self, user_id: int):
        """
        List all permissions associated with an user.

        Args:
            user_id [int]:
        """
        msg = "Function not implemented"
        raise exceptions.PumpWoodNotImplementedError(
            message=msg)


class PumpwoodPermissionPolicyAction(models.Model):
    """Permission Policies to customize action access.

    Custom action permission can allow/deny specific actions associated with
    a model class.
    """

    """Pumpwood PermissionPolicy ."""

    PERMISSION_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
    ]

    policy = models.ForeignKey(
        PumpwoodPermissionPolicy, on_delete=models.CASCADE,
        related_name="action_set", verbose_name="Policy",
        help_text="Permission")
    action = models.CharField(
        max_length=154, null=False, blank=False,
        verbose_name="Route action",
        help_text="Route action to which apply permission")
    permission = models.TextField(
        choices=PERMISSION_CHOICES, null=False, blank=False,
        verbose_name="Allow/Deny",
        help_text="If user can run or not this action")
    extra_info = models.JSONField(
        default=dict, blank=True,
        verbose_name="Extra info.",
        help_text="Other information that can be usefull",
        encoder=PumpWoodJSONEncoder)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True,
        related_name='policy_action_updated_by_set',
        verbose_name="Updated By",
        help_text="Updated By")
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")

    class Meta:
        db_table = 'api_permission__policy_action'
        unique_together = [['policy', 'action'], ]

        verbose_name = 'Custom Action Policy'
        verbose_name_plural = 'Custom Action Policies'


class PumpwoodPermissionGroup(models.Model):
    """Permission group for Pumpwood End-Points."""

    description = models.TextField(
        null=False, unique=True, blank=False,
        verbose_name="Description",
        help_text="A short description of the route.")
    notes = models.TextField(
        null=False, default="", blank=True,
        verbose_name="Notes",
        help_text="A long description of the route.")
    dimensions = models.JSONField(
        default=dict, blank=True,
        verbose_name="Dimentions",
        help_text="Dictionary of tags to help organization",
        encoder=PumpWoodJSONEncoder)
    extra_info = models.JSONField(
        default=dict, blank=True,
        verbose_name="Extra info.",
        help_text="Other information that can be usefull",
        encoder=PumpWoodJSONEncoder)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True,
        related_name='permission_group_updated_by_set',
        verbose_name="Updated By",
        help_text="Updated By")
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")

    class Meta:
        db_table = 'api_permission__group'
        verbose_name = 'Permission Group'
        verbose_name_plural = 'Permission Groups'


class PumpwoodPermissionUserGroupM2M(models.Model):
    """Permission group user association."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="api_permission_group_set",
        verbose_name="User",
        help_text="User associated with group")
    group = models.ForeignKey(
        PumpwoodPermissionGroup, on_delete=models.CASCADE,
        related_name="group_user_set", verbose_name="Group",
        help_text="Permission Group to apply policy")
    extra_info = models.JSONField(
        default=dict, blank=True,
        verbose_name="Extra info.",
        help_text="Other information that can be usefull",
        encoder=PumpWoodJSONEncoder)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True,
        related_name='permission_user_group_updated_by_set',
        verbose_name="Updated By",
        help_text="Updated By")
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")

    class Meta:
        db_table = 'api_permission__user_group_m2m'
        unique_together = [['user', 'group', ], ]

        verbose_name = 'Permission User -> Group'
        verbose_name_plural = 'Permission User -> Group'


class PumpwoodPermissionPolicyGroupM2M(models.Model):
    """Link PermissionPolicy and PumpwoodPermissionGroup."""

    PERMISSION_CHOICES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('custom', 'Custom'),
    ]

    priority = models.IntegerField(
        null=False, default=0, verbose_name="Policy priority",
        help_text="Policy priority, lower number will have precedence")
    group = models.ForeignKey(
        PumpwoodPermissionGroup, on_delete=models.CASCADE,
        related_name="permission_set", verbose_name="Group",
        help_text="Permission Group to apply policy")
    general_policy = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="General Permission",
        help_text="Read/Write general permission")
    custom_policy = models.ForeignKey(
        PumpwoodPermissionPolicy, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="policy_group_set", verbose_name="Group",
        help_text="Pemission Policy that will be applied to the group")
    extra_info = models.JSONField(
        default=dict, blank=True,
        verbose_name="Extra info",
        help_text="Other information that can be usefull",
        encoder=PumpWoodJSONEncoder)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True,
        related_name='permission_group_updated_by_m2m_set',
        verbose_name="Updated By",
        help_text="Updated By")
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")

    class Meta:
        db_table = 'api_permission__policy_group_m2m'
        verbose_name = 'Permission Policy -> Group'
        verbose_name_plural = 'Permission Policy -> Group'


class PumpwoodPermissionPolicyUserM2M(models.Model):
    """Link PermissionPolicy and User."""

    PERMISSION_CHOICES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('custom', 'Custom'),
    ]

    priority = models.IntegerField(
        null=False, default=0, verbose_name="Policy priority",
        help_text="Policy priority, lower number will have precedence")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="api_permission_set",
        verbose_name="User",
        help_text="Permission Group to apply policy")
    general_policy = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="General Permission",
        help_text="Read/Write general policy")
    custom_policy = models.ForeignKey(
        PumpwoodPermissionPolicy, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="policy_user_set", verbose_name="Custom Policy",
        help_text="Custom policy that will be applied to the group")
    extra_info = models.JSONField(
        default=dict, blank=True,
        verbose_name="Extra info.",
        help_text="Other information that can be usefull",
        encoder=PumpWoodJSONEncoder)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False, blank=True,
        related_name='permission_user_updated_by_m2m_set',
        verbose_name="Updated By",
        help_text="Updated By")
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")

    class Meta:
        db_table = 'api_permission__policy_user_m2m'
        verbose_name = 'Permission Policy -> User'
        verbose_name_plural = 'Permission Policy -> User'
