# Generated by Django 2.2 on 2020-12-26 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunchapp', '0004_auto_20201225_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plannedmenu',
            name='uuid_menu',
            field=models.CharField(default='fff92b44-0834-4f65-bca0-54c8cf0a0eaa', editable=False, max_length=50, unique=True, verbose_name='UUID Menu'),
        ),
    ]
