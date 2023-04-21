from django.urls import path

from common.apis import version

app_name = "version"
urlpatterns = [
    path("", version.VersionView.as_view(), name="index"),
    path(
        "upgrade_frontend", version.UpgradeFrontend.as_view(), name="upgrade_frontend"
    ),
]
