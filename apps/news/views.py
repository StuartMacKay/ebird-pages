import datetime as dt
import re

from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.translation import get_language
from django.views import generic

from dateutil.relativedelta import MO, relativedelta
from ebird.codes.locations import is_country_code, is_county_code, is_state_code

from data.models import Country, County, District


class IndexView(generic.TemplateView):
    template_name = "news/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        week = self.request.GET.get("week", "")
        code = self.request.GET.get("code", "")
        search = self.request.GET.get("search", "")

        if week:
            week_start = dt.datetime.strptime("%s-1" % week, "%Y-%W-%w").date()
        else:
            week_start = timezone.now().date() - relativedelta(weekday=MO(-1))

        week_end = week_start + relativedelta(days=6)

        if week_start.month == week_end.month:
            subtitle = "%s - %s" % (format(week_start, "d"), format(week_end, "d M Y"))
        else:
            if week_start.year == week_end.year:
                subtitle = "%s - %s" % (
                    format(week_start, "d M"),
                    format(week_end, "d M Y"),
                )
            else:
                subtitle = "%s - %s" % (
                    format(week_start, "d M Y"),
                    format(week_end, "d M Y"),
                )

        if get_language() == "pt":
            subtitle = subtitle.lower()

        last_week = week_start - relativedelta(days=1)
        next_week = week_start + relativedelta(days=7)

        country = district = county = None

        if is_country_code(code):
            country = Country.objects.get(code=code).pk
        elif is_state_code(code):
            district = District.objects.get(code=code).pk
        elif is_county_code(code):
            county = County.objects.get(code=code).pk

        context["country"] = country
        context["district"] = district
        context["county"] = county
        context["search"] = search
        context["week_start"] = week_start
        context["week_end"] = week_end + relativedelta(days=1)
        context["this_week"] = week_start.strftime("%Y-%W")
        context["start_year"] = week_start.year
        context["end_year"] = week_end.year
        context["last_week"] = last_week.strftime("%Y-%W")
        context["next_week"] = next_week.strftime("%Y-%W")
        context["subtitle"] = subtitle
        context["show_country"] = Country.objects.all().count() > 1

        return context


def autocomplete(request):
    """
    Return the list of countries, regions and districts for the search
    field. If there is only one country, remove it from the label.
    """
    data = []

    for code, place in Country.objects.all().values_list("code", "place"):
        data.append({"value": code, "label": place})

    if len(data) == 1:
        country = data.pop(0)["label"]
    else:
        country = None

    for code, place in District.objects.all().values_list("code", "place"):
        if country:
            label = re.sub(r", %s$" % country, "", place)
        else:
            label = place
        data.append({"value": code, "label": label})

    for code, place in County.objects.all().values_list("code", "place"):
        if country:
            label = re.sub(r", %s$" % country, "", place)
        else:
            label = place
        data.append({"value": code, "label": label})

    return JsonResponse(data, safe=False)
