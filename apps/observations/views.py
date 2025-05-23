import datetime as dt

from django.views import generic

from django_filters.views import FilterView

from data.models import Country, Observation, Observer

from .filters import ObservationFilter


class ObservationsView(FilterView):
    model = Observation
    filterset_class = ObservationFilter
    template_name = "observations/index.html"
    paginate_by = 100
    ordering = ("-started",)

    def get_queryset(self):
        related = ["country", "state", "county", "location", "observer", "species"]
        queryset = super().get_queryset().select_related(*related)
        return self.filterset_class(self.request.GET, queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_country"] = Country.objects.all().count() > 1
        return context


class BigDayView(generic.ListView):
    model = Observation
    template_name = "observations/big-day.html"
    context_object_name = "observations"
    ordering = ("-started",)

    def get_filters(self):
        filters = {
            "observer": self.request.GET.get("observer"),
            "date": self.request.GET.get("date"),
        }

        return filters

    def get_queryset(self):
        qs = super().get_queryset()
        filters = self.get_filters()

        qs = qs.filter(observer__identifier=filters["observer"])
        qs = qs.filter(date=filters["date"])

        return qs.select_related(
            "country",
            "state",
            "county",
            "location",
            "observer",
            "species",
        ).order_by('species__taxon_order')

    def get_context_data(self, **kwargs):
        filters = self.get_filters()
        context = super().get_context_data(**kwargs)
        context["date"] = dt.datetime.strptime(filters["date"], "%Y-%m-%d")
        context["observer"] = Observer.objects.get(identifier=filters["observer"])
        return context
