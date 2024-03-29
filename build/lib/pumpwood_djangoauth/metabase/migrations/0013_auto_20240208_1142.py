# Generated by Django 3.2.6 on 2024-02-08 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('metabase', '0012_auto_20240205_1154'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='metabasedashboard',
            options={'verbose_name': ('P', 'u', 'm', 'p', 'w', 'o', 'o', 'd', ' ', 'M', 'e', 't', 'a', 'b', 'a', 's', 'e', ' ', 'D', 'a', 's', 'h', 'b', 'o', 'r', 'd'), 'verbose_name_plural': ('P', 'u', 'm', 'p', 'w', 'o', 'o', 'd', ' ', 'M', 'e', 't', 'a', 'b', 'a', 's', 'e', ' ', 'D', 'a', 's', 'h', 'b', 'o', 'r', 'd', 's')},
        ),
        migrations.AlterModelOptions(
            name='metabasedashboardparameter',
            options={'verbose_name': ('M', 'e', 't', 'a', 'b', 'a', 's', 'e', ' ', 'D', 'a', 's', 'h', 'b', 'o', 'a', 'r', 'd', ' ', 'P', 'a', 'r', 'a', 'm', 'e', 't', 'e', 'r'), 'verbose_name_plural': ('M', 'e', 't', 'a', 'b', 'a', 's', 'e', ' ', 'D', 'a', 's', 'h', 'b', 'o', 'a', 'r', 'd', ' ', 'P', 'a', 'r', 'a', 'm', 'e', 't', 'e', 'r', 's')},
        ),
        migrations.AlterField(
            model_name='metabasedashboard',
            name='auto_embedding',
            field=models.BooleanField(default=False, help_text=('A', 'u', 't', 'o', ' ', 'e', 'm', 'b', 'e', 'd', 'd', ' ', 'd', 'a', 's', 'h', 'b', 'o', 'a', 'r', 'd', ' ', 'a', 't', ' ', 'f', 'r', 'o', 'n', 't', '-', 'e', 'n', 'd'), verbose_name=('A', 'u', 't', 'o', ' ', 'e', 'm', 'b', 'e', 'd', 'd', 'i', 'n', 'g')),
        ),
        migrations.AlterField(
            model_name='metabasedashboard',
            name='description',
            field=models.CharField(help_text=('D', 'a', 's', 'h', 'b', 'o', 'a', 'r', 'd', ' ', 'd', 'e', 's', 'c', 'r', 'i', 'p', 't', 'i', 'o', 'n'), max_length=100, unique=True, verbose_name=('D', 'e', 's', 'c', 'r', 'i', 'p', 't', 'i', 'o', 'n')),
        ),
        migrations.AlterField(
            model_name='metabasedashboard',
            name='expire_in_min',
            field=models.IntegerField(default=10, help_text=('M', 'i', 'n', 'u', 't', 'e', 's', ' ', 't', 'o', ' ', 'e', 'x', 'p', 'i', 'r', 'e', ' ', 'u', 'r', 'l'), verbose_name=('E', 'x', 'p', 'i', 'r', 'a', 't', 'i', 'o', 'n', ' ', 'p', 'e', 'r', 'i', 'o', 'd')),
        ),
        migrations.AlterField(
            model_name='metabasedashboard',
            name='metabase_id',
            field=models.IntegerField(help_text=('M', 'e', 't', 'a', 'b', 'a', 's', 'e', ' ', 'D', 'a', 's', 'h', 'b', 'o', 'a', 'r', 'd', ' ', 'I', 'd'), verbose_name=('M', 'e', 't', 'a', 'b', 'a', 's', 'e', ' ', 'I', 'D')),
        ),
        migrations.AlterField(
            model_name='metabasedashboard',
            name='notes',
            field=models.TextField(blank=True, default='', help_text=('A', ' ', 'l', 'o', 'n', 'g', ' ', 'd', 'e', 's', 'c', 'r', 'i', 'p', 't', 'i', 'o', 'n', ' ', 'o', 'f', ' ', 't', 'h', 'e', ' ', 'd', 'a', 's', 'h', 'b', 'o', 'a', 'r', 'd'), verbose_name=('N', 'o', 't', 'e', 's')),
        ),
        migrations.AlterField(
            model_name='metabasedashboard',
            name='object_pk',
            field=models.IntegerField(blank=True, help_text=('O', 'b', 'j', 'e', 'c', 't', ' ', 'P', 'K', ' ', 'a', 's', 's', 'o', 'c', 'i', 'a', 't', 'e', 'd', ' ', 'w', 'i', 't', 'h', ' ', 'd', 'a', 's', 'h', 'b', 'o', 'a', 'r', 'd'), null=True, verbose_name=('O', 'b', 'j', 'e', 'c', 't', ' ', 'P', 'K')),
        ),
        migrations.AlterField(
            model_name='metabasedashboard',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, help_text=('U', 'p', 'd', 'a', 't', 'e', 'd', ' ', 'A', 't'), verbose_name=('U', 'p', 'd', 'a', 't', 'e', 'd', ' ', 'A', 't')),
        ),
        migrations.AlterField(
            model_name='metabasedashboard',
            name='updated_by',
            field=models.ForeignKey(blank=True, help_text=('U', 'p', 'd', 'a', 't', 'e', 'd', ' ', 'B', 'y'), on_delete=django.db.models.deletion.CASCADE, related_name='metabase_dash_set', to=settings.AUTH_USER_MODEL, verbose_name=('U', 'p', 'd', 'a', 't', 'e', 'd', ' ', 'B', 'y')),
        ),
        migrations.AlterField(
            model_name='metabasedashboardparameter',
            name='dashboard',
            field=models.ForeignKey(help_text=('D', 'a', 's', 'h', 'b', 'o', 'a', 'r', 'd', ' ', 'a', 's', 's', 'o', 'c', 'i', 'a', 't', 'e', 'd', ' ', 'w', 'i', 't', 'h', ' ', 'p', 'a', 'r', 'a', 'm', 'e', 'n', 't', 'e', 'r', 's'), on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set', to='metabase.metabasedashboard', verbose_name=('P', 'u', 'm', 'p', 'w', 'o', 'o', 'd', ' ', 'M', 'e', 't', 'a', 'b', 'a', 's', 'e', ' ', 'D', 'a', 's', 'h', 'b', 'o', 'r', 'd')),
        ),
        migrations.AlterField(
            model_name='metabasedashboardparameter',
            name='notes',
            field=models.TextField(blank=True, default='', help_text=('a', ' ', 'l', 'o', 'n', 'g', ' ', 'd', 'e', 's', 'c', 'r', 'i', 'p', 't', 'i', 'o', 'n', ' ', 'o', 'f', ' ', 't', 'h', 'e', ' ', 'p', 'a', 'r', 'a', 'm', 'e', 't', 'e', 'r'), verbose_name=('a', ' ', 'l', 'o', 'n', 'g', ' ', 'd', 'e', 's', 'c', 'r', 'i', 'p', 't', 'i', 'o', 'n', ' ', 'o', 'f', ' ', 't', 'h', 'e', ' ', 'p', 'a', 'r', 'a', 'm', 'e', 't', 'e', 'r')),
        ),
    ]
