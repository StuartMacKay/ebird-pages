from django.db import models
from django.utils.translation import gettext_lazy as _


class County(models.Model):
    class Meta:
        verbose_name = _("county")
        verbose_name_plural = _("counties")

    code = models.CharField(
        max_length=10,
        db_index=True,
        verbose_name=_("code"),
        help_text=_("The code used to identify the county."),
    )

    name = models.TextField(
        verbose_name=_("name"), help_text=_("The name of the county.")
    )

    place = models.TextField(
        verbose_name=_("place"), help_text=_("The hierarchical name of the county.")
    )

    def __repr__(self) -> str:
        return str(self.code)

    def __str__(self) -> str:
        return str(self.name)
