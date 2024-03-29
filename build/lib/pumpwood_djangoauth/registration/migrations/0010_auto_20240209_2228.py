# Generated by Django 3.2.6 on 2024-02-09 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0009_auto_20240205_1154'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pumpwoodmfacode',
            options={'verbose_name': 'MFA code', 'verbose_name_plural': 'MFA codes'},
        ),
        migrations.AlterModelOptions(
            name='pumpwoodmfamethod',
            options={'verbose_name': 'MFA Method', 'verbose_name_plural': 'MFA Methods'},
        ),
        migrations.AlterModelOptions(
            name='pumpwoodmfarecoverycode',
            options={'verbose_name': 'MFA recovery code', 'verbose_name_plural': 'MFA recovery codes'},
        ),
        migrations.AlterModelOptions(
            name='pumpwoodmfatoken',
            options={'verbose_name': 'MFA Token', 'verbose_name_plural': 'MFA Tokens'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'User profile', 'verbose_name_plural': 'Users profile'},
        ),
    ]
