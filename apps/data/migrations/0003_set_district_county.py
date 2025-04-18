# Generated by Django 5.1.4 on 2025-04-11 12:16

from django.db import migrations

def copy_district_to_county(apps, schema_editor):
    District = apps.get_model("data", "District")
    County = apps.get_model("data", "County")

    for district in District.objects.all():
        county = County.objects.create(
            code=district.code,
            name=district.name,
            place=district.place
        )

        for location in district.locations.all():
            location.county = county
            location.district = None
            location.save()

        for checklist in district.checklists.all():
            checklist.county = county
            checklist.district = None
            checklist.save()

        for observation in district.observations.all():
            observation.county = county
            observation.district = None
            observation.save()

    District.objects.all().delete()


def copy_region_to_district(apps, schema_editor):
    Region = apps.get_model("data", "Region")
    District = apps.get_model("data", "District")

    for region in Region.objects.all():
        district = District.objects.create(
            code=region.code,
            name=region.name,
            place=region.place
        )

        for location in region.locations.all():
            location.district = district
            location.region = None
            location.save()

        for checklist in region.checklists.all():
            checklist.district = district
            checklist.region = None
            checklist.save()

        for observation in region.observations.all():
            observation.district = district
            observation.region = None
            observation.save()

    Region.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "data",
            "0002_add_state_county",
        ),
    ]

    operations = [
        migrations.RunPython(copy_district_to_county),
        migrations.RunPython(copy_region_to_district),
    ]
