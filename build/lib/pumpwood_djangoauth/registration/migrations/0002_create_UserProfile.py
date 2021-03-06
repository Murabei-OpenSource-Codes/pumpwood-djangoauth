# Generated by Django 3.2.6 on 2022-01-19 21:08

from django.db import migrations


def create_UserProfile(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    UserProfile = apps.get_model('registration', 'UserProfile')
    User = apps.get_model('auth', 'User')

    for user in User.objects.all().order_by("id"):
        UserProfile(
            user=user,
            is_microservice="microservice" in user.username
        ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
    ]
