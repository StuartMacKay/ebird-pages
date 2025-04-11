# pyright: reportArgumentType=false

from django.db import models
from django.utils.translation import gettext_lazy as _


class State(models.Model):
    class Meta:
        verbose_name = _("state")
        verbose_name_plural = _("states")

    code = models.CharField(
        max_length=10,
        db_index=True,
        verbose_name=_("code"),
        help_text=_("The code used to identify the state."),
    )

    name = models.TextField(
        verbose_name=_("name"), help_text=_("The name of the state.")
    )

    place = models.TextField(
        verbose_name=_("place"), help_text=_("The hierarchical name of the state.")
    )

    def __str__(self):
        return str(self.name)
