"""Expand Django users to set more information and password reset."""
import os
import hashlib
import random
import datetime
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from pumpwood_communication.serializers import PumpWoodJSONEncoder
from pumpwood_communication.exceptions import (
    PumpWoodForbidden, PumpWoodMFAError)
from pumpwood_djangoauth.registration.mfa_aux.main import send_mfa_code
from pumpwood_djangoauth.i8n.translate import t


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name=t(
            "User",
            tag="UserProfile__admin__user"),
        help_text=t(
            "User",
            tag="UserProfile__admin__user"),
        related_name="user_profile")
    is_service_user = models.BooleanField(
        default=False,
        verbose_name=t(
            "Is service User?",
            tag="UserProfile__admin__is_service_user"),
        help_text=t(
            "If user is a service user to comnicate programatically",
            tag="UserProfile__admin__is_service_user"))
    dimensions = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        verbose_name=t(
            "Dimentions",
            tag="UserProfile__admin__dimensions"),
        help_text=t(
            "Key/value tags to help retrieve database information",
            tag="UserProfile__admin__dimensions"))
    extra_fields = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        verbose_name=t(
            "Extra Info",
            tag="UserProfile__admin__default"),
        help_text=t(
            "Extra Info",
            tag="UserProfile__admin__default"))

    class Meta:
        db_table = 'pumpwood__userprofile'
        verbose_name = t(
            'User profile',
            tag="UserProfile__admin")
        verbose_name_plural = t(
            'Users profile',
            tag="UserProfile__admin", plural=True)


class PumpwoodMFAMethod(models.Model):
    """Set MFA associated with user."""

    TYPES = [
        ('sms', 'SMS'),
    ]
    is_enabled = models.BooleanField(
        default=True,
        verbose_name=t(
            "If MFA is enabled?",
            tag="PumpwoodMFAMethod__admin__is_enabled"),
        help_text=t(
            "Unable MFA will not be used to validate login",
            tag="PumpwoodMFAMethod__admin__is_enabled"))
    is_validated = models.BooleanField(
        default=False,
        verbose_name=t(
            "If MFA is validated?",
            tag="PumpwoodMFAMethod__admin__is_validated"),
        help_text=t(
            "Unvalidated MFA will not be used on login",
            tag="PumpwoodMFAMethod__admin__is_validated"))
    msg = models.TextField(
        default="", null=False, blank=True,
        verbose_name=t(
            "MFA message?",
            tag="PumpwoodMFAMethod__admin__msg"),
        help_text=t(
            "Message from MFA validation",
            tag="PumpwoodMFAMethod__admin__msg"))
    priority = models.PositiveIntegerField(
        null=False,
        verbose_name=t(
            "MFA Priority",
            tag="PumpwoodMFAMethod__admin__priority"),
        help_text=t(
            "MFA method priority",
            tag="PumpwoodMFAMethod__admin__priority"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="mfa_method_set",
        verbose_name=t(
            "User",
            tag="PumpwoodMFAMethod__admin__user"),
        help_text=t(
            "User associated with MFA",
            tag="PumpwoodMFAMethod__admin__user"))
    type = models.CharField(
        max_length=10, choices=TYPES,
        verbose_name=t(
            "MFA Type",
            tag="PumpwoodMFAMethod__admin__type"),
        help_text=t(
            "Type of the MFA that will be used for validation",
            tag="PumpwoodMFAMethod__admin__type"))
    mfa_parameter = models.CharField(
        max_length=200, blank=True,
        verbose_name=t(
            "MFA Parameter",
            tag="PumpwoodMFAMethod__admin__mfa_parameter"),
        help_text=t((
            "MFA Parameter can be telephone, email, ... depending "
            "of the MFA Method"),
            tag="PumpwoodMFAMethod__admin__mfa_parameter"))
    extra_info = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        verbose_name=t(
            "Extra info.",
            tag="PumpwoodMFAMethod__admin__extra_info"),
        help_text=t((
            "Extra information for MFA method"),
            tag="PumpwoodMFAMethod__admin__extra_info"))

    class Meta:
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
            validation_mfacode = PumpwoodMFACode(
                token=validation_mfa, mfa_method=self)
            validation_mfacode.save()
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


class PumpwoodMFAToken(models.Model):
    """Create MFA token when user login and it has MFA enabled."""

    token = models.CharField(
        max_length=64, primary_key=True,
        verbose_name=t(
            "MFA Token",
            tag="PumpwoodMFAToken__admin__token"),
        help_text=t((
            "MFA Token to validate MFA code request validation"),
            tag="PumpwoodMFAToken__admin__token"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="mfa_token_set",
        verbose_name=t(
            "User",
            tag="PumpwoodMFAToken__admin__user"),
        help_text=t((
            "User assciated with MFA token"),
            tag="PumpwoodMFAToken__admin__user"))
    created_at = models.DateTimeField(
        null=False, blank=True,
        verbose_name=t(
            "Created at",
            tag="PumpwoodMFAToken__admin__created_at"),
        help_text=t((
            "Time was created at"),
            tag="PumpwoodMFAToken__admin__created_at"))
    expire_at = models.DateTimeField(
        null=False, blank=True,
        verbose_name=t(
            "Expire at",
            tag="PumpwoodMFAToken__admin__expire_at"),
        help_text=t((
            "MFA token will expire at"),
            tag="PumpwoodMFAToken__admin__expire_at"))

    class Meta:
        db_table = 'pumpwood__mfa_token'
        verbose_name = t(
            'MFA Token',
            tag="PumpwoodMFAToken__admin")
        verbose_name_plural = t(
            'MFA Tokens',
            tag="PumpwoodMFAToken__admin", plural=True)

    def save(self, *args, **kwargs):
        """Ovewrite save to create primary key and set expire date."""
        if not self.pk:
            self.created_at = timezone.now()

            rand_str = str(random.randint(0, 9999999999)).zfill(10)
            m = hashlib.sha256((
                self.created_at.isoformat() + '|' + rand_str).encode())
            self.token = m.hexdigest()

            EXPIRATION_INTERVAL = int(os.getenv(
                "PUMPWOOD__MFA__TOKEN_EXPIRATION_INTERVAL", 60*5))
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
    """
    Code associated with MFA session.

    It does not have expire date and will respect MFA token expire datetime.
    """

    token = models.ForeignKey(
        PumpwoodMFAToken, on_delete=models.CASCADE,
        related_name="mfa_code_set",
        verbose_name=t(
            "MFA Token",
            tag="PumpwoodMFACode__admin__token"),
        help_text=t((
            "MFA Token foreign key"),
            tag="PumpwoodMFACode__admin__token"))
    mfa_method = models.ForeignKey(
        PumpwoodMFAMethod, on_delete=models.CASCADE,
        related_name="mfa_code_set",
        verbose_name=t(
            "MFA Method foreign key",
            tag="PumpwoodMFACode__admin__mfa_method"),
        help_text=t((
            "MFA Method associated with code"),
            tag="PumpwoodMFACode__admin__mfa_method"))
    code = models.CharField(
        max_length=6, null=False, blank=True,
        verbose_name=t(
            "MFA Code",
            tag="PumpwoodMFACode__admin__code"),
        help_text=t((
            "6 digit MFA code"),
            tag="PumpwoodMFACode__admin__code"))
    created_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name=t(
            "Created At",
            tag="PumpwoodMFACode__admin__created_at"),
        help_text=t((
            "Time was created at"),
            tag="PumpwoodMFACode__admin__created_at"))

    class Meta:
        db_table = 'pumpwood__mfa_code'
        verbose_name = t(
            'MFA code',
            tag="PumpwoodMFACode__admin")
        verbose_name_plural = t(
            'MFA codes',
            tag="PumpwoodMFACode__admin", plural=True)

    def save(self, *args, **kwargs):
        """Create MFA Code."""
        if self.pk is None:
            self.code = str(random.randint(0, 999999)).zfill(6)

        # Do not let update MFA codes
        else:
            msg = "It is not possible to update MFA codes, only create."
            raise PumpWoodForbidden(msg)

        # Send MFA code according to method choosen by the user
        send_mfa_code(mfa_method=self.mfa_method, code=self.code)
        super(PumpwoodMFACode, self).save(*args, **kwargs)


class PumpwoodMFARecoveryCode(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="recovery_codes_set",
        verbose_name=t(
            "User",
            tag="PumpwoodMFACode__admin__created_at"),
        help_text=t((
            "User foreign key"),
            tag="PumpwoodMFACode__admin__created_at"))
    code = models.CharField(
        max_length=8, null=False, blank=True,
        verbose_name=t(
            "Recovery Code",
            tag="PumpwoodMFACode__admin__created_at"),
        help_text=t((
            "8 digits recovery code"),
            tag="PumpwoodMFACode__admin__created_at"))
    created_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name=t(
            "Recovery Code",
            tag="PumpwoodMFACode__admin__created_at"),
        help_text=t((
            "Time was created at"),
            tag="PumpwoodMFACode__admin__created_at"))

    class Meta:
        db_table = 'pumpwood__mfa_recovery_code'
        verbose_name = t(
            'MFA recovery code',
            tag="PumpwoodMFACode__admin")
        verbose_name_plural = t(
            'MFA recovery codes',
            tag="PumpwoodMFACode__admin", plural=True)
