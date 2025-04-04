# pyright: reportArgumentType=false

from django.db import models
from django.utils.translation import gettext_lazy as _


class Area(models.Model):
    class Meta:
        verbose_name = _("area")
        verbose_name_plural = _("areas")

    code = models.CharField(
        max_length=6,
        db_index=True,
        verbose_name=_("code"),
        help_text=_("The code used to identify the area."),
    )

    name = models.TextField(
        verbose_name=_("name"), help_text=_("The name of the area.")
    )

    place = models.TextField(
        verbose_name=_("place"), help_text=_("The hierarchical name of the area.")
    )

    def __str__(self):
        return str(self.name)
