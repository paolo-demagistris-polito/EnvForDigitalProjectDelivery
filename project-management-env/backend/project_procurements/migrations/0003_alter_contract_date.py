# Generated by Django 4.0.3 on 2022-06-18 13:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('project_procurements', '0002_alter_contract_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
