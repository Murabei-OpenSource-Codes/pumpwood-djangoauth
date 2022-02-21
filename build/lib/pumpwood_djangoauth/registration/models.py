"""Expand Django users to set more information and password reset."""
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from pumpwood_communication.serializers import PumpWoodJSONEncoder


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        UserProfile.objects.create(user=instance)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="user_profile")

    is_microservice = models.BooleanField(
        default=False,
        help_text="If user is a service user to comnicate programatically.")
    dimentions = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        help_text="Dictionary to help query users on database.")
    extra_fields = models.JSONField(
        default=dict, blank=True, encoder=PumpWoodJSONEncoder,
        help_text="Extra information for the user.")

    class Meta:
        db_table = 'pumpwood__userprofile'
