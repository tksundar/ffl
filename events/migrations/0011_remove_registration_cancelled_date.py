# Generated by Django 3.1 on 2020-08-30 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_auto_20200830_1412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='cancelled_date',
        ),
    ]