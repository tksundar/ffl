# Generated by Django 3.1 on 2020-08-27 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='login',
            name='temp_password',
            field=models.CharField(default='', max_length=10),
        ),
    ]
