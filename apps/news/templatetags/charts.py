from dateutil.relativedelta import relativedelta
from django import template
from django.db import connection
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from checklists.models import Checklist

register = template.Library()


@register.inclusion_tag("news/charts/protocol-pie-chart.html")
def protocol_pie_chart():
    today = timezone.now().date()
    one_week_ago = today - relativedelta(days=7)

    data: list[int] = []
    labels: list = []

    for code, label in (
        ("P20", _("Incidental")),
        ("P21", _("Stationary")),
        ("P22", _("Traveling")),
    ):
        data.append(
            Checklist.objects.filter(date__gt=one_week_ago, protocol_code=code).count()
        )
        labels.append(label)

    if (
        other := Checklist.objects.filter(date__gt=one_week_ago)
        .exclude(protocol_code__in=["P20", "P21", "P22"])
        .count()
    ):
        data.append(other)
        labels.append(_("Other"))

    return {"label": _("Number of checklists"), "labels": labels, "data": data}


@register.inclusion_tag("news/charts/checklist-species.html")
def checklist_species_chart(country_id, region_id, district_id, start, end):
    queryset = Checklist.objects.filter(date__gte=start, date__lt=end)

    with connection.cursor() as cursor:
        if country_id:
            filter = f"and country_id = {country_id} "
            queryset = queryset.filter(country_id=country_id)
        elif region_id:
            filter = f"and region_id = {region_id} "
            queryset = queryset.filter(region_id=region_id)
        elif district_id:
            filter = f"and district_id = {district_id} "
            queryset = queryset.filter(district_id=district_id)
        else:
            filter = ""

        total = queryset.count()

        cursor.execute(
            f"select "
            f"count(*), "
            f"((species_count - 1) / 5)::int as quantile "
            f"from checklists_checklist "
            f"where date >= '{start}' "
            f"and date < '{end}' "
            f"and species_count > 0 "
            f"{filter} "
            f"group by quantile"
        )

        result = sorted(cursor.fetchall(), key=lambda t: t[1])

        data: list[int] = []
        labels: list[str] = []

        for count, index in result:
            start = index * 5 + 1
            end = start + 4
            data.append(round((count * 100) / total, 1))
            labels.append("%d-%d" % (start, end))

    return {
        "xaxis_title": _("Number of species"),
        "yaxis_title": _("Percentage of checklists"),
        "label": _("Percentage"),
        "labels": labels,
        "data": data,
    }
