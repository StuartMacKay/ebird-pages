# Generated by Django 5.1.4 on 2025-04-12 07:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0006_set_observation_time"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="location",
            name="atlas_block",
        ),
        migrations.RemoveField(
            model_name="location",
            name="bcr_code",
        ),
        migrations.RemoveField(
            model_name="location",
            name="iba_code",
        ),
        migrations.RemoveField(
            model_name="location",
            name="type",
        ),
        migrations.RemoveField(
            model_name="location",
            name="usfws_code",
        ),
    ]
