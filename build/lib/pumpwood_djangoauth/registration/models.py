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


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="user_profile")
    is_service_user = models.BooleanField(
        default=False,
        help_text="If user is a service user to comnicate programatically.")
    dimensions = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        help_text="Dictionary to help query users on database.")
    extra_fields = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        help_text="Extra information for the user.")

    class Meta:
        db_table = 'pumpwood__userprofile'


class PumpwoodMFAMethod(models.Model):
    """Set MFA associated with user."""

    TYPES = [
        ('sms', 'SMS'),
    ]
    is_enabled = models.BooleanField(
        default=True, help_text="If MFA is enabled")
    is_validated = models.BooleanField(
        default=False, help_text="If MFA is enabled")
    msg = models.TextField(
        help_text="Message from MFA validation", default="",
        null=False, blank=True)
    priority = models.PositiveIntegerField(
        null=False, help_text="MFA method priority")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="mfa_method_set")
    type = models.CharField(
        max_length=10, choices=TYPES,
        help_text="User MFA")
    mfa_parameter = models.CharField(
        max_length=200, help_text="MFA Parameter. Telephone, email, etc...",
        blank=True)
    extra_info = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        help_text="MFA extra information")

    class Meta:
        db_table = 'pumpwood__mfa'
        unique_together = [
            ['user_id', 'type'],
            ['user_id', 'priority']
        ]

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
        max_length=64, help_text="MFA Token", primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="mfa_token_set", help_text="User foreign key")
    created_at = models.DateTimeField(
        null=False, blank=True, help_text="Time was created at")
    expire_at = models.DateTimeField(
        null=False, blank=True, help_text="Time it will expire at")

    class Meta:
        db_table = 'pumpwood__mfa_token'

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
        help_text="PumpwoodMFAToken foreign key")
    mfa_method = models.ForeignKey(
        PumpwoodMFAMethod, on_delete=models.CASCADE,
        related_name="mfa_code_set",
        help_text="PumpwoodMFAMethod foreign key")
    code = models.CharField(
        max_length=6, null=False, blank=True,
        help_text="6 digit MFA code")
    created_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        help_text="Time was created at")

    class Meta:
        db_table = 'pumpwood__mfa_code'

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
        help_text="User foreign key")
    code = models.CharField(
        max_length=8, null=False, blank=True,
        help_text="8 digits recovery code")
    created_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        help_text="Time was created at")

    class Meta:
        db_table = 'pumpwood__mfa_recovery_code'
