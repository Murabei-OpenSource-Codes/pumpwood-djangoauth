"""Expand Django users to set more information and password reset."""
import os
import hashlib
import random
import datetime
from typing import List
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from pumpwood_communication.serializers import PumpWoodJSONEncoder
from pumpwood_communication.exceptions import (
    PumpWoodForbidden, PumpWoodMFAError, PumpWoodNotImplementedError,
    PumpWoodActionArgsException)
from pumpwood_djangoviews.action import action
from pumpwood_djangoauth.registration.mfa_aux.message_delivery import (
    send_mfa_code)
from pumpwood_djangoauth.i8n.translate import t

# Auxiliary classes and functions
from pumpwood_djangoauth.registration.aux import (
    ApiPermissionAux, RowPermissionAux)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_profile(sender, instance=None, created=False, **kwargs):
    """Create a auth profile when user is created."""
    if created:
        UserProfile.objects.create(user=instance)


class UserProfile(models.Model):
    """User profile with extra information."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name="User", help_text="User",
        related_name="user_profile")
    is_service_user = models.BooleanField(
        default=False,
        verbose_name="Is service User?",
        help_text="If user is a service user to comnicate programatically")
    dimensions = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        verbose_name="Dimentions",
        help_text="Key/value tags to help retrieve database information")
    extra_fields = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        verbose_name="Extra Info",
        help_text="Extra Info")

    class Meta:
        """Meta class."""
        db_table = 'pumpwood__userprofile'
        verbose_name = 'User profile'
        verbose_name_plural = 'Users profile'

    @classmethod
    @action(info="List self assciated API permissions",
            request='request')
    def self_api_permissions(cls, request) -> List[dict]:
        """List users api permissions.

        Args:
            request:
                Django request.
        """
        return ApiPermissionAux.get(user=request.user, request=request)

    @classmethod
    @action(info="List user's assciated API permissions",
            request='request')
    def user_api_permissions(cls, user_id: int, request) -> List[dict]:
        """List users api permissions.

        Args:
            user_id (int):
                User's id associated with API permissions.
            request:
                Django request.
        """
        User = get_user_model() # NOQA
        user = User.objects.get(id=user_id)
        return ApiPermissionAux.get(user=user, request=request)

    @classmethod
    @action(info="List user's assciated API permissions",
            request='request')
    def self_row_permissions(cls, request) -> List[dict]:
        """List users api permissions.

        Args:
            request:
                Django request.
        """
        user = request.user
        return RowPermissionAux.get(user=user, request=request)

    @classmethod
    @action(info="List user's assciated API permissions",
            request='request')
    def user_row_permissions(cls, user_id: int, request) -> List[dict]:
        """List users api permissions.

        Args:
            user_id (int):
                User's id associated with API permissions.
            request:
                Django request.
        """
        User = get_user_model() # NOQA
        user = User.objects.get(id=user_id)
        return RowPermissionAux.get(user=user, request=request)

    @classmethod
    @action(info="List user's assciated API permissions",
            request='request')
    def create_user(cls, request, username: str, password: str, email: str,
                    first_name: str, last_name: str, is_active: bool = True,
                    is_staff: bool = False, is_superuser: bool = False,
                    profile_is_service_user: bool = False,
                    profile_dimensions: dict = {},
                    profile_extra_fields: dict = {}) -> dict:
        """List users api permissions.

        Args:
            request:
                Django request.
            username (str):
                User name of the new user.
            password (str):
                Password of the new user.
            email (str):
                Email associated with new user.
            first_name (str):
                First name of the new user.
            last_name (str):
                Last name of the new user.
            is_active (bool):
                If user will be created as active.
            is_staff (bool):
                If user will have access to admin site.
            is_superuser (bool):
                If user will be considered a superuser.
            profile_is_service_user (bool):
                If user will be considered a service user. Service users are
                used for inter Pumpwood calls. Any login atempt from outside
                of the cluster of a service user will be blocked.
            profile_dimensions (dict):
                Key/Value dimentions (tags) associated with user, this can be
                used better organizate users on database.
            profile_extra_fields (dict):
                Extra information.
        """
        # Import serialized in fuction to not make circular imports
        from pumpwood_djangoauth.registration.serializers import (
            SerializerUser)
        User = get_user_model() # NOQA

        # Validate password complexity before user creation, it is necessary
        # to use a user instance to validate password
        temp_user = User(
            username=username, email=email,
            first_name=first_name, is_active=is_active,
            is_staff=is_staff, is_superuser=is_superuser)
        try:
            validate_password(password, user=temp_user)
        except ValidationError as e:
            msg = "Password did not respect complexity rules:\n{password}"
            raise PumpWoodActionArgsException(
                message=msg, payload={"password": list(e.messages)})

        # Create the user object
        user = User.objects.create(
            username=username, email=email,
            first_name=first_name, is_active=is_active,
            is_staff=is_staff, is_superuser=is_superuser)
        # Set user password
        user.set_password(password)

        # set profile information
        user_profile = user.user_profile
        user_profile.is_service_user = profile_is_service_user
        user_profile.dimensions = profile_dimensions
        user_profile.extra_fields = profile_extra_fields
        user_profile.save()
        return_data = SerializerUser(user, context={'request': request}).data
        return return_data


class PumpwoodMFAMethod(models.Model):
    """Set MFA associated with user."""

    TYPES = [
        ('sms', 'SMS'),
        ('sso', 'Single Sign-On'),
    ]

    is_enabled = models.BooleanField(
        default=True,
        verbose_name="If MFA is enabled?",
        help_text="Unable MFA will not be used to validate login")
    is_validated = models.BooleanField(
        default=False,
        verbose_name="If MFA is validated?",
        help_text="Unvalidated MFA will not be used on login")
    msg = models.TextField(
        default="", null=False, blank=True,
        verbose_name="MFA message?",
        help_text="Message from MFA validation")
    priority = models.PositiveIntegerField(
        null=False,
        verbose_name="MFA Priority",
        help_text="MFA method priority")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="mfa_method_set",
        verbose_name="User",
        help_text="User associated with MFA")
    type = models.CharField(
        max_length=10, choices=TYPES,
        verbose_name="MFA Type",
        help_text="Type of the MFA that will be used for validation")
    mfa_parameter = models.CharField(
        max_length=200, blank=True,
        verbose_name="MFA Parameter",
        help_text=(
            "MFA Parameter can be telephone, email, ... depending "
            "of the MFA Method"))
    extra_info = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        verbose_name=t(
            "Extra info.",
            tag="PumpwoodMFAMethod__admin__extra_info"),
        help_text=t((
            "Extra information for MFA method"),
            tag="PumpwoodMFAMethod__admin__extra_info"))

    class Meta:
        """Meta class."""
        db_table = 'pumpwood__mfa'
        unique_together = [
            ['user_id', 'type'],
            ['user_id', 'priority']
        ]
        verbose_name = t(
            'MFA Method',
            tag="PumpwoodMFAMethod__admin")
        verbose_name_plural = t(
            'MFA Methods',
            tag="PumpwoodMFAMethod__admin", plural=True)

    def save(self, *args, **kwargs):
        """Validate creation of MFA when saving object."""
        # Validate MFA Method for user
        validation_mfa = PumpwoodMFAToken(user=self.user)
        validation_mfa.save()

        try:
            # Check if it is possible to create a MFACode
            super(PumpwoodMFAMethod, self).save(*args, **kwargs)
            self.run_method(mfa_token=validation_mfa.token)

            self.is_validated = True
            self.msg = "MFA validated"
            super(PumpwoodMFAMethod, self).save(*args, **kwargs)

        except PumpWoodMFAError as e:
            # If creation of a MFA Code leads to a PumpWoodMFAError
            # than set method as not validated and will be not used
            # on loging
            self.is_validated = False
            self.msg = e.message
            super(PumpwoodMFAMethod, self).save(*args, **kwargs)

    def run_method(self, mfa_token: str):
        """Run MFA method.

        Args:
            mfa_token (str):
                MFA Token.
        Kwargs:
            No Kwargs.
        Return [dict]:
            pass
        """
        from pumpwood_djangoauth.registration.mfa_aux.views.oauth2 import (
            create_sso_client)

        validation_mfa = PumpwoodMFAToken.objects.filter(
            token=mfa_token).first()
        if validation_mfa is None:
            msg = "MFA token not found"
            raise PumpWoodMFAError(msg)

        # Create an MFA Code and send it using an sms broker
        if self.type == 'app_log':
            new_code = PumpwoodMFACode(token=validation_mfa, mfa_method=self)
            new_code.save()
            return {"code_status": "logged"}

        # Create an MFA Code and send it using an sms broker
        if self.type == 'sms':
            new_code = PumpwoodMFACode(token=validation_mfa, mfa_method=self)
            new_code.save()
            return {"code_status": "sent"}

        # Create an redirect URL for SSO autorization
        if self.type == 'sso':
            sso_client = create_sso_client()
            authorization_url = sso_client.create_authorization_url(
                state=validation_mfa.token)
            return {"authorization_url": authorization_url}

        msg = "Method {method} not implemented"
        raise PumpWoodNotImplementedError(
            msg, payload={"method": self.type})

        return {
            'mfa_method_type': self.type,
            'mfa_method_result': {
                'authorization_url': authorization_url['authorization_url']
            },
            'expiry': validation_mfa.expire_at,
            'mfa_token': validation_mfa.token}


class PumpwoodMFAToken(models.Model):
    """Create MFA token when user login and it has MFA enabled."""

    token = models.CharField(
        max_length=64, primary_key=True,
        verbose_name="MFA Token",
        help_text=(
            "MFA Token to validate MFA code request validation"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="mfa_token_set",
        verbose_name="User",
        help_text=("User assciated with MFA token"))
    created_at = models.DateTimeField(
        null=False, blank=True,
        verbose_name="Created at",
        help_text=("Time was created at"))
    expire_at = models.DateTimeField(
        null=False, blank=True,
        verbose_name="Expire at",
        help_text=("MFA token will expire at"))

    class Meta:
        """Meta."""
        db_table = 'pumpwood__mfa_token'
        verbose_name = 'MFA Token'
        verbose_name_plural = 'MFA Tokens'

    def save(self, *args, **kwargs):
        """Ovewrite save to create primary key and set expire date."""
        if not self.pk:
            self.created_at = timezone.now()

            rand_str = str(random.randint(0, 9999999999)).zfill(10) # NOQA
            m = hashlib.sha256((
                self.created_at.isoformat() + '|' + rand_str).encode())
            self.token = m.hexdigest()

            EXPIRATION_INTERVAL = int(os.getenv(  # NOQA
                "PUMPWOOD__MFA__TOKEN_EXPIRATION_INTERVAL", 60 * 5))
            expiration_time = (
                self.created_at +
                datetime.timedelta(seconds=EXPIRATION_INTERVAL))
            self.expire_at = expiration_time

        # Do not let update MFA tokens
        else:
            msg = "It is not possible to update MFA tokens, only create."
            raise PumpWoodForbidden(msg)
        super(PumpwoodMFAToken, self).save(*args, **kwargs)


class PumpwoodMFACode(models.Model):
    """Code associated with MFA session.

    It does not have expire date and will respect MFA token expire datetime.
    """

    token = models.ForeignKey(
        PumpwoodMFAToken, on_delete=models.CASCADE,
        related_name="mfa_code_set",
        verbose_name="MFA Token",
        help_text="MFA Token foreign key")
    mfa_method = models.ForeignKey(
        PumpwoodMFAMethod, on_delete=models.CASCADE,
        related_name="mfa_code_set",
        verbose_name="MFA Method foreign key",
        help_text="MFA Method associated with code")
    code = models.CharField(
        max_length=6, null=False, blank=True,
        verbose_name="MFA Code",
        help_text="6 digit MFA code")
    created_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Created At",
        help_text="Time was created at")

    class Meta:
        """Meta."""
        db_table = 'pumpwood__mfa_code'
        verbose_name = 'MFA code'
        verbose_name_plural = 'MFA codes'

    def save(self, *args, **kwargs):
        """Create MFA Code."""
        if self.pk is None:
            self.code = str(random.randint(0, 999999)).zfill(6) # NOQA

        # Do not let update MFA codes
        else:
            msg = "It is not possible to update MFA codes, only create."
            raise PumpWoodForbidden(msg)

        # Send MFA code according to method choosen by the user
        send_mfa_code(mfa_method=self.mfa_method, code=self.code)
        super().save(*args, **kwargs)


class PumpwoodMFARecoveryCode(models.Model):
    """Pumpwood MFA recovery codes."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="recovery_codes_set",
        verbose_name="User",
        help_text="User foreign key")
    code = models.CharField(
        max_length=8, null=False, blank=True,
        verbose_name="Recovery Code",
        help_text="8 digits recovery code")
    created_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name="Recovery Code",
        help_text="Time was created at")

    class Meta:
        """Meta."""
        db_table = 'pumpwood__mfa_recovery_code'
        verbose_name = 'MFA recovery code'
        verbose_name_plural = 'MFA recovery codes'
