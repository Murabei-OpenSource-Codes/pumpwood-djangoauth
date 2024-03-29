# Generated by Django 3.2.6 on 2023-10-24 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metabase', '0006_auto_20231024_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metabasedashboard',
            name='status',
            field=models.CharField(choices=[('inactive', 'Archived'), ('dev', 'Development'), ('homolog', 'Homologation'), ('production', 'Production')], help_text='Status', max_length=15, verbose_name='Status'),
        ),
    ]
