from django import template
from django.db.models import Avg, Case, Count, F, Min, Q, Sum, When
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta

from data.models import Checklist, Observation, Observer, Species

register = template.Library()


@register.inclusion_tag("news/tables/big-lists.html")
def big_lists_table(country_id, state_id, county_id, start, end, show_country):
    queryset = Checklist.objects.filter(date__gte=start, date__lte=end)

    if country_id:
        queryset = queryset.filter(country_id=country_id)
    elif state_id:
        queryset = queryset.filter(state_id=state_id)
    elif county_id:
        queryset = queryset.filter(county_id=county_id)

    related = ["state", "county", "location", "observer"]

    if show_country:
        related.append("country")

    checklists = queryset.select_related(*related).order_by("-species_count")[:10]

    return {
        "title": _("Big Lists"),
        "checklists": sorted(list(checklists), key=lambda checklist: checklist.started),
    }


@register.inclusion_tag("news/tables/checklists-submitted.html")
def checklists_submitted_table(country_id, state_id, county_id, start, end):
    queryset = Checklist.objects.filter(date__gte=start, date__lte=end)

    if country_id:
        queryset = queryset.filter(country_id=country_id)
    elif state_id:
        queryset = queryset.filter(state_id=state_id)
    elif county_id:
        queryset = queryset.filter(county_id=county_id)

    observers = (
        queryset.values("observer")
        .annotate(name=F("observer__name"))
        .annotate(byname=F("observer__byname"))
        .annotate(count=Count("observer"))
        .filter(complete=True)
        .order_by("-count")
    )[:10]

    return {"records": observers}


@register.inclusion_tag("news/tables/checklists-duration.html")
def checklists_duration_table(country_id, state_id, county_id, start, end):
    queryset = Checklist.objects.filter(date__gte=start, date__lte=end)

    if country_id:
        queryset = queryset.filter(country_id=country_id)
    elif state_id:
        queryset = queryset.filter(state_id=state_id)
    elif county_id:
        queryset = queryset.filter(county_id=county_id)

    observers = (
        queryset.values("observer")
        .annotate(name=F("observer__name"))
        .annotate(byname=F("observer__byname"))
        .annotate(total=Sum("duration"))
        .filter(duration__isnull=False)
        .order_by("-total")
    )[:10]

    for observer in observers:
        observer["hours"] = "%0d" % (observer["total"] / 60)
        observer["minutes"] = "%02d" % (observer["total"] % 60)

    return {"records": observers}


@register.inclusion_tag("news/tables/checklists-species.html")
def checklists_species_table(country_id, state_id, county_id, start, end):
    filters = Q(observations__date__gte=start)
    filters &= Q(observations__date__lte=end)
    filters &= Q(
        observations__species__category__in=["species", "sub-species", "domestic"]
    )

    if country_id:
        filters &= Q(observations__country_id=country_id)
    elif state_id:
        filters &= Q(observations__state_id=state_id)
    elif county_id:
        filters &= Q(observations__county_id=county_id)

    observers = (
        Observer.objects.values("name", "byname")
        .annotate(
            count=Count(
                Case(
                    When(
                        filters,
                        then="observations__species",
                    )
                ),
                distinct=True,
            )
        )
        .order_by("-count")[:10]
    )
    return {"records": [observer for observer in observers if observer["count"]]}


@register.inclusion_tag("news/tables/yearlist.html", takes_context=True)
def yearlist_table(context):
    filters = Q()

    if context.get("country"):
        filters &= Q(observations__country_id=context["country"])
    elif context.get("state"):
        filters &= Q(observations__state_id=context["state"])
    elif context.get("county"):
        filters &= Q(observations__county_id=context["county"])

    species = Species.objects.filter(category="species")

    if filters:
        species = species.annotate(
            added=Min(Case(When(filters, then="observations__date")))
        )
    else:
        species = species.annotate(added=Min("observations__date"))

    species = species.filter(
        added__gte=context["start_date"], added__lte=context["end_date"]
    ).order_by("added")

    observations = []

    filters = Q()

    if context.get("country"):
        filters &= Q(country_id=context["country"])
    elif context.get("state"):
        filters &= Q(state_id=context["state"])
    elif context.get("county"):
        filters &= Q(county_id=context["county"])

    for item in species:
        observations.append(
            Observation.objects.filter(date=item.added, species_id=item.pk)
            .filter(filters)
            .select_related(
                "checklist",
                "country",
                "state",
                "county",
                "location",
                "species",
                "observer",
            )
            .first()
        )

    total = (
        Observation.objects.filter(filters)
        .filter(species__category="species")
        .filter(date__lte=context["end_date"], date__year=context["year"])
        .distinct()
        .values("species_id")
        .count()
    )

    return {
        "title": _("Year List"),
        "year": str(context["year"]),
        "observations": observations,
        "total": total,
        "show_country": context["show_country"],
    }


@register.inclusion_tag("news/tables/big-days.html")
def big_days_table(country_id, state_id, county_id, start, end):
    queryset = (
        Observation.objects.values("observer__identifier", "date")
        .annotate(name=F("observer__name"))
        .annotate(species_count=Count("species", distinct=True))
        .filter(date__gte=start, date__lte=end)
    )

    if country_id:
        queryset = queryset.filter(country_id=country_id)
    elif state_id:
        queryset = queryset.filter(state_id=state_id)
    elif county_id:
        queryset = queryset.filter(county_id=county_id)

    entries = queryset.order_by("-species_count")[:10]

    return {
        "title": _("Big Days"),
        "entries": sorted(list(entries), key=lambda entry: entry["date"]),
    }


@register.inclusion_tag("news/tables/high-counts.html", takes_context=True)
def high_counts_table(context):
    filters = Q()

    if context.get("country"):
        filters &= Q(country_id=context["country"])
    elif context.get("state"):
        filters &= Q(state_id=context["state"])
    elif context.get("county"):
        filters &= Q(county_id=context["county"])

    species = {}

    records = (
        Observation.objects.values_list("species_id", "count")
            .filter(filters)
            .filter(
                species__category="species",
                date__lt=context["start_date"],
                date__gte=context["start_date"] - relativedelta(months=1),
                count__isnull=False,
            )
            .order_by("species__taxon_order", "-count")
    )

    for record in records:
        if record[0] not in species:
            species[record[0]] = [record[1]]
        elif len(species[record[0]]) == 1 and record[1] < species[record[0]][0]:
            species[record[0]].append(record[1])
        else:
            continue

    for id, counts in species.items():
        species[id] = counts[-1]

    observations = []

    for species_id, count in species.items():
        observation = (
            Observation.objects.filter(filters)
            .filter(
                species_id=species_id,
                count__gt=count,
                date__gte=context["start_date"],
                date__lte=context["end_date"],
            )
            .select_related("species", "location", "observer")
            .order_by("-count")
            .first()
        )
        if observation:
            observations.append(observation)

    return {
        "observations": observations,
        "show_country": context["show_country"],
    }
