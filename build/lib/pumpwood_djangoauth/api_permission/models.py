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
        - **description [TextField]:**
            Unique description for PumpwoodPermissionPolicy objects.
        - **notes [TextField]:** Long descriptions for
            PumpwoodPermissionPolicy objects.
        - **dimensions [JSONField]:** Key/Value dictionary with
            information to help organization/fetch of the data.
        - **route [ForeignKey('KongRoute')]:** ForeignKey
            to KongRoute model_class. It corresponds to the route at which
            the permission policy will be applied.
        - **can_list [choices]:** Permissions associated with list end-point
            for this policy. Options as avaiable at `PERMISSION_CHOICES`.
        - **can_list_without_pag [choices]:** Permissions associated with
            list-without-pag end-point for this policy. Options as avaiable at
            `PERMISSION_CHOICES`.
        - **can_retrieve [choices]:** Permissions associated with
            retrieve end-point for this policy. Options as avaiable at
            `PERMISSION_CHOICES`.
        - **can_retrieve_file [choices]:** Permissions associated with
            retrieve file end-point for this policy. Options as avaiable at
            `PERMISSION_CHOICES`.
        - **can_delete [choices]:** Permissions associated with
            delete end-point for this policy. Options as avaiable at
            `PERMISSION_CHOICES`.
        - **can_delete_many [choices]:** Permissions associated with
            delete many end-point for this policy. Options as avaiable at
            `PERMISSION_CHOICES`.
        - **can_delete_file [TextField]:** Permissions associated with
            delete file end-point for this policy. Options as avaiable at
            `PERMISSION_CHOICES`.
        - **can_save [TextField]:** Permissions associated with
            save end-point for this policy. Options as avaiable at
            `PERMISSION_CHOICES`.
        - **can_run_actions [TextField]:** Permissions associated with
            execute action end-point for this policy. Options as avaiable at
            `ACTION_PERMISSION_CHOICES`. Custom action policy can be created
            to fine grained policy permission associated with each action
            using PumpwoodPermissionPolicyAction model class.
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
    """@private"""
    route = models.ForeignKey(
        'system.KongRoute', on_delete=models.CASCADE,
        related_name="permission_set", verbose_name="Route",
        help_text="Route associated with permission.")
    """@private"""
    can_list = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="List",
        help_text="Permission to list end-point and front-end page")
    """@private"""
    can_list_without_pag = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="List Without Pag.",
        help_text=(
            "Permission to list without pagination end-point. Return all "
            "values associated with query (list paginate 50)"))
    """@private"""
    can_retrieve = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Retrieve",
        help_text="Permission to retrieve end-point and front-end page")
    """@private"""
    can_retrieve_file = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Retrieve File",
        help_text="Permission to retrieve file end-point")
    """@private"""
    can_delete = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Delete",
        help_text="Permission to delete object end-point and front-end page")
    """@private"""
    can_delete_many = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Delete Many",
        help_text="Permission to delete many end-point")
    """@private"""
    can_delete_file = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Delete File",
        help_text="Permission to delelte file end-point")
    """@private"""
    can_save = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="Save",
        help_text="Permission to save end-point and front-end page")
    """@private"""
    can_run_actions = models.TextField(
        choices=ACTION_PERMISSION_CHOICES,
        default="no_change", verbose_name="Actions",
        help_text="Permission to run actions")
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
        related_name='policy_updated_by_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """@private"""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """@private"""

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'api_permission__policy'
        verbose_name = 'Permission Policy'
        verbose_name_plural = 'Permission Policies'

    @classmethod
    def list_user_permissions(self, user_pk: int) -> list:
        """
        List all permissions associated with an user.

        .. warning::
            Function not implemented yet.

        Args:
            user_pk [int]:
                User pk tho whom list all avaiable
                permissions.
        Raises:
            PumpWoodNotImplementedError:
                Function is not implemented.
        """
        msg = "Function not implemented"
        raise exceptions.PumpWoodNotImplementedError(
            message=msg)


class PumpwoodPermissionPolicyAction(models.Model):
    """Permission Policies to customize action access.

    Custom action permission can allow/deny specific actions associated with
    a model class.

    Model fields:
        - **policy [ForeignKey('PumpwoodPermissionPolicy')]:** Foreign
            key associated with `PumpwoodPermissionPolicy`. It will
            create fine grained permission policy associated with custom
            policy for action execution.
        - **action [CharField]:** Name of the action over which policy will
            be applied.
        - **permission [choices]:** Choices associated with policy. Choices
            limited to `PERMISSION_CHOICES` options.
        - **extra_info [JSONField]:** Exta information that might be usefull.
        - **updated_by [ForeignKey('User')]:** User associated with
            creation/update of the action custom policy.
        - **updated_at [DateTimeField]:** Date/time associated with creation/
            update of the policy.
    """

    PERMISSION_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
    ]
    """Choices associated with custom action policy."""

    policy = models.ForeignKey(
        PumpwoodPermissionPolicy, on_delete=models.CASCADE,
        related_name="action_set", verbose_name="Policy",
        help_text="Permission")
    """@private"""
    action = models.CharField(
        max_length=154, null=False, blank=False,
        verbose_name="Route action",
        help_text="Route action to which apply permission")
    """@private"""
    permission = models.TextField(
        choices=PERMISSION_CHOICES, null=False, blank=False,
        verbose_name="Allow/Deny",
        help_text="If user can run or not this action")
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
        related_name='policy_action_updated_by_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """@private"""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """@private"""

    class Meta:
        db_table = 'api_permission__policy_action'
        unique_together = [['policy', 'action'], ]
        """Fields to be considered that should be considered unique together
           on the database.."""
        verbose_name = 'Custom Action Policy'
        verbose_name_plural = 'Custom Action Policies'


class PumpwoodPermissionGroup(models.Model):
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
        related_name='permission_group_updated_by_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """@private"""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """@private"""

    class Meta:
        db_table = 'api_permission__group'
        verbose_name = 'Permission Group'
        verbose_name_plural = 'Permission Groups'


class PumpwoodPermissionUserGroupM2M(models.Model):
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
        User, on_delete=models.CASCADE,
        related_name="api_permission_group_set",
        verbose_name="User",
        help_text="User associated with group")
    """@private"""
    group = models.ForeignKey(
        PumpwoodPermissionGroup, on_delete=models.CASCADE,
        related_name="group_user_set", verbose_name="Group",
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
        related_name='permission_user_group_updated_by_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """@private"""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """@private"""

    class Meta:
        db_table = 'api_permission__user_group_m2m'
        unique_together = [['user', 'group', ], ]

        verbose_name = 'Permission User -> Group'
        verbose_name_plural = 'Permission User -> Group'


class PumpwoodPermissionPolicyGroupM2M(models.Model):
    """Link PermissionPolicy and PumpwoodPermissionGroup.

    Associate permission policies with groups to apply it to all users
    that belongs to the group.

    Model fields:
        - **priority [IntegerField]:** Integer setting priority to permission
            policy. Lower numbers with have priority.
        - **group [ForeignKey('PumpwoodPermissionGroup')]:** Foreign Key to
            associated policy with group.
        - **general_policy [TextField]:** General policy associate with group,
            it will affect all Pumpwood end-points.
        - **custom_policy [ForeignKey]:** Foreign Key to associate a
            PumpwoodPermissionPolicy to a PumpwoodPermissionGroup.
        - **extra_info [JSONField]:** Extra information that might be
            important.
        - **updated_by [ForeignKey]:** User that created/updated the relation
            between PumpwoodPermissionGroup and policies
        - **updated_at [DateTimeField]:** Date/time the relation was created/
            updated.
    """

    PERMISSION_CHOICES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('custom', 'Custom'),
    ]
    """Choices for general permission that are associated with all pumpwood
       end-points."""

    priority = models.IntegerField(
        null=False, default=0, verbose_name="Policy priority",
        help_text="Policy priority, lower number will have precedence")
    """@private"""
    group = models.ForeignKey(
        PumpwoodPermissionGroup, on_delete=models.CASCADE,
        related_name="permission_set", verbose_name="Group",
        help_text="Permission Group to apply policy")
    """@private"""
    general_policy = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="General Permission",
        help_text="Read/Write general permission")
    """@private"""
    custom_policy = models.ForeignKey(
        PumpwoodPermissionPolicy, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="policy_group_set", verbose_name="Group",
        help_text="Pemission Policy that will be applied to the group")
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
        related_name='permission_group_updated_by_m2m_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """@private"""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """@private"""

    class Meta:
        db_table = 'api_permission__policy_group_m2m'
        verbose_name = 'Permission Policy -> Group'
        verbose_name_plural = 'Permission Policy -> Group'


class PumpwoodPermissionPolicyUserM2M(models.Model):
    """Link PermissionPolicy and User.

    Associate permission policies with users individualy.

    Model class:
        - **priority [IntegerField]:** Integer setting priority to permission
            policy. Lower numbers with have priority.
        - **user [ForeignKey('user')]:** Foreign Key to
            associated policy with user.
        - **general_policy [TextField]:** General policy associate with group,
            it will affect all Pumpwood end-points.
        - **custom_policy [ForeignKey]:** Foreign Key to associate a
            PumpwoodPermissionPolicy to a PumpwoodPermissionGroup.
        - **extra_info [JSONField]:** Extra information that might be
            important.
        - **updated_by [ForeignKey]:** User that created/updated the relation
            between PumpwoodPermissionGroup and policies
        - **updated_at [DateTimeField]:** Date/time the relation was created/
            updated.
    """

    PERMISSION_CHOICES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('custom', 'Custom'),
    ]
    """Choices for general permission that are associated with all pumpwood
       end-points."""

    priority = models.IntegerField(
        null=False, default=0, verbose_name="Policy priority",
        help_text="Policy priority, lower number will have precedence")
    """@private"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="api_permission_set",
        verbose_name="User",
        help_text="Permission Group to apply policy")
    """@private"""
    general_policy = models.TextField(
        choices=PERMISSION_CHOICES,
        default="no_change", verbose_name="General Permission",
        help_text="Read/Write general policy")
    """@private"""
    custom_policy = models.ForeignKey(
        PumpwoodPermissionPolicy, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="policy_user_set", verbose_name="Custom Policy",
        help_text="Custom policy that will be applied to the group")
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
        related_name='permission_user_updated_by_m2m_set',
        verbose_name="Updated By",
        help_text="Updated By")
    """@private"""
    updated_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Updated At",
        help_text="Updated At")
    """@private"""

    class Meta:
        db_table = 'api_permission__policy_user_m2m'
        verbose_name = 'Permission Policy -> User'
        verbose_name_plural = 'Permission Policy -> User'
