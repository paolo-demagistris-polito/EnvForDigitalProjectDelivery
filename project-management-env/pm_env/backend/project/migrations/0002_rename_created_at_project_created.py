# Generated by Django 4.0.3 on 2022-04-18 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='created_at',
            new_name='created',
        ),
    ]
