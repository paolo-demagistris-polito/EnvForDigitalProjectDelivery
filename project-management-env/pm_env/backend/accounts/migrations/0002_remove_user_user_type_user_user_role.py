# Generated by Django 4.0.3 on 2022-04-22 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='user_type',
        ),
        migrations.AddField(
            model_name='user',
            name='user_role',
            field=models.CharField(choices=[('PMO', 'PMO'), ('PM', 'PM'), ('PS', 'PS'), ('PC', 'PC'), ('PSC', 'PSC'), ('PP', 'PP'), ('AS', 'AS'), ('U', 'U')], default='U', max_length=3),
        ),
    ]
