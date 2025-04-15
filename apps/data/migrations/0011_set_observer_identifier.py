# Generated by Django 5.1.4 on 2025-04-15 10:49
import socket

from django.db import migrations

from ebird.scrapers import get_checklist

socket.setdefaulttimeout(30)

def set_observer_identifier(apps, schema_editor):
    Observer = apps.get_model("data", "Observer")

    for observer in Observer.objects.filter(identifier=""):
        for checklist in observer.checklists.all():
            try:
                data = get_checklist(checklist.identifier)
                observer.identifier = data["observer"]["identifier"]
                observer.save()
                break
            except:  # noqa
                pass

class Migration(migrations.Migration):

    dependencies = [
        ("data", "0010_set_observation_started"),
    ]

    operations = [
        migrations.RunPython(set_observer_identifier),
    ]
