from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class Config(AppConfig):
    label = "_checklists"
    name = "checklists"
    verbose_name = _("Checklists")
