# Generated by Django 4.0.3 on 2022-04-18 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_project_oa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='oa',
        ),
    ]
