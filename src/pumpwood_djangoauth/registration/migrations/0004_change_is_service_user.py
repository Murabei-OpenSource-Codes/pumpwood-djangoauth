# Generated by Django 3.2.6 on 2023-11-05 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_ajust_misspelling'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='is_microservice',
            new_name='is_service_user',
        ),
    ]
