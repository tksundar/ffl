# Generated by Django 3.1 on 2020-08-30 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_auto_20200830_1345'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registration',
            old_name='is_deleted',
            new_name='cancelled',
        ),
        migrations.AddField(
            model_name='registration',
            name='cancelled_date',
            field=models.DateField(default=None),
        ),
    ]
