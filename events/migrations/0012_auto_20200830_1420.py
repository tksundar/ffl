# Generated by Django 3.1 on 2020-08-30 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_remove_registration_cancelled_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registration',
            old_name='cancelled',
            new_name='is_deleted',
        ),
    ]
