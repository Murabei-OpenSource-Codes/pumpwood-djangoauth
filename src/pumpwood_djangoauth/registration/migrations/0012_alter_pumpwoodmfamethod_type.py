# Generated by Django 3.2.6 on 2024-05-07 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0011_auto_20240209_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pumpwoodmfamethod',
            name='type',
            field=models.CharField(choices=[('sms', 'SMS'), ('sso', 'Single Sign-On')], help_text='Type of the MFA that will be used for validation', max_length=10, verbose_name='MFA Type'),
        ),
    ]