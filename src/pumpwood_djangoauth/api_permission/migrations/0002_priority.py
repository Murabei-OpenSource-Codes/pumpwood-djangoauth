# Generated by Django 3.2.6 on 2024-03-12 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_permission', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pumpwoodpermissionpolicygroupm2m',
            name='priority',
            field=models.IntegerField(default=0, help_text='Policy priority, lower number will have precedence', verbose_name='Policy priority'),
        ),
        migrations.AddField(
            model_name='pumpwoodpermissionpolicyuserm2m',
            name='priority',
            field=models.IntegerField(default=0, help_text='Policy priority, lower number will have precedence', verbose_name='Policy priority'),
        ),
    ]
