# Generated by Django 3.2.6 on 2023-06-16 23:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pumpwood_communication.serializers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MetabaseDashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('inactive', 'Archived'), ('homolog', 'Homologation'), ('production', 'Production')], help_text='Status', max_length=15, verbose_name='Status')),
                ('description', models.CharField(help_text='service url to redirect the http calls.', max_length=100, unique=True)),
                ('notes', models.TextField(blank=True, default='', help_text='a long description of the dashboard.')),
                ('metabase_id', models.IntegerField(help_text='Metabase Dashboard Id.')),
                ('expire_in_min', models.IntegerField(default=10, help_text='Minutes to expire url.')),
                ('default_theme', models.CharField(choices=[('light', 'light'), ('night', 'dark'), ('transparent', 'transparent')], default='light', help_text='Theme', max_length=15, verbose_name='Theme')),
                ('default_is_bordered', models.BooleanField(default=False, help_text='Is Bordered?', verbose_name='Is bordered?')),
                ('default_is_titled', models.BooleanField(default=False, help_text='Is titled?', verbose_name='Is titled?')),
                ('dimensions', models.JSONField(blank=True, default=dict, encoder=pumpwood_communication.serializers.PumpWoodJSONEncoder, help_text='Key/Value Dimentions', verbose_name='Dimentions')),
                ('extra_info', models.JSONField(blank=True, default=dict, encoder=pumpwood_communication.serializers.PumpWoodJSONEncoder, help_text='Extra information', verbose_name='Extra information')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Created At', verbose_name='Created At')),
                ('updated_by', models.ForeignKey(blank=True, help_text='Created By', on_delete=django.db.models.deletion.CASCADE, related_name='metabase_dash_set', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
            ],
            options={
                'db_table': 'metabase__dashboard',
            },
        ),
        migrations.CreateModel(
            name='MetabaseDashboardParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('str', 'String'), ('datetime', 'Data/Time'), ('int', 'Integer'), ('float', 'Float'), ('user_id', 'Request User Id')], help_text='Type', max_length=15, verbose_name='Type')),
                ('name', models.CharField(help_text='Parameter name', max_length=50, verbose_name='Parameter name')),
                ('notes', models.TextField(blank=True, default='', help_text='a long description of the parameter.')),
                ('default_value', models.CharField(blank=True, help_text='Default value', max_length=100, null=True, verbose_name='Default value')),
                ('dashboard', models.ForeignKey(help_text='Dashboard associated with paramenters.', on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set', to='metabase.metabasedashboard')),
            ],
            options={
                'db_table': 'metabase__dashboard_parameter',
                'unique_together': {('dashboard', 'name')},
            },
        ),
    ]
