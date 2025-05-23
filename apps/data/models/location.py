from django.db import models
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")

    identifier = models.TextField(
        unique=True,
        verbose_name=_("identifier"),
        help_text=_("The unique identifier for the location"),
    )

    name = models.TextField(
        verbose_name=_("name"), help_text=_("The name of the location")
    )

    byname = models.TextField(
        blank=True,
        default="",
        verbose_name=_("byname"),
        help_text=_("The display name of the location"),
    )

    country = models.ForeignKey(
        "data.Country",
        related_name="locations",
        on_delete=models.PROTECT,
        verbose_name=_("country"),
        help_text=_("The country for the location."),
    )

    state = models.ForeignKey(
        "data.State",
        related_name="locations",
        on_delete=models.PROTECT,
        verbose_name=_("state"),
        help_text=_("The state for the location."),
    )

    county = models.ForeignKey(
        "data.County",
        blank=True,
        null=True,
        related_name="locations",
        on_delete=models.PROTECT,
        verbose_name=_("county"),
        help_text=_("The county for the location."),
    )

    latitude = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=7,
        max_digits=9,
        verbose_name=_("latitude"),
        help_text=_("The decimal latitude of the location, relative to the equator"),
    )

    longitude = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=7,
        max_digits=10,
        verbose_name=_("longitude"),
        help_text=_(
            "The decimal longitude of the location, relative to the prime meridian"
        ),
    )

    url = models.URLField(
        blank=True,
        verbose_name=_("url"),
        help_text=_("URL of the location page on eBird."),
    )

    hotspot = models.BooleanField(
        blank=True,
        null=True,
        verbose_name=_("is hotspot"),
        help_text=_("Is the location a hotspot"),
    )

    data = models.JSONField(
        verbose_name=_("Data"),
        help_text=_("Data describing a Location"),
        default=dict,
        blank=True,
    )

    def __repr__(self) -> str:
        return str(self.identifier)

    def __str__(self) -> str:
        return self.display_name()

    def display_name(self):
        return str(self.byname or self.name)
