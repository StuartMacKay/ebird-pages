from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from apps.dashboards.views import IndexView

urlpatterns = i18n_patterns(
    path("", IndexView.as_view(), name="index"),
    path(_("checklists/"), include("checklists.urls")),
    path(_("dashboards/"), include("dashboards.urls")),
    path(_("observations/"), include("observations.urls")),
)

urlpatterns += [
    # Change the path to the Django Admin to something non-standard.
    path(settings.ADMIN_PATH, admin.site.urls),  # type: ignore
    path("watchman/", include("watchman.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DJANGO_ENV == "development" and settings.DEBUG:
    from django.views import defaults

    urlpatterns += [
        path(
            "403/",
            defaults.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            defaults.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path(
            "500/",
            defaults.server_error,
        ),
    ]

    # Add a view that raises and error to test sentry in development
    def trigger_error(request):
        raise Exception("Verify Sentry is configured and working")

    urlpatterns += [
        path("__debug__/sentry/", trigger_error),
    ]

    import debug_toolbar  # type: ignore

    urlpatterns += [
        path("__debug__/toolbar/", include(debug_toolbar.urls)),  # type: ignore
    ]
