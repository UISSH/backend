"""UISSH URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import logging

import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from dockers.apis.image import DockerImageView
from dockers.apis.volume import DockerVolumeView
from rest_framework.routers import DefaultRouter

from common import views
from common.apis import opreating, user
from common.apis.kv_storage import KVStorageView
from crontab.apis.main import CrontabViewSet
from database.apis import database
from dockers.apis.main import DockerContainerView
from filebrowser.apis.filebrowser import FileBrowserView
from ftpserver.apis.ftpserver import FtpServerView
from iptables.apis.main import IPTablesView
from terminal.apis.main import TerminalView
from webdav.apis.webdav import WebDAVView
from website.apis import application, website

router = DefaultRouter()
router.register(r"User", user.UserView)
router.register(r"Operating", opreating.OperatingView, basename="Operating")
router.register(r"Website", website.WebsiteView)
router.register(r"Application", application.ApplicationView, basename="Application")
router.register(r"DataBase", database.DataBaseView)
router.register(r"Admin/User", user.AdminUserView)
router.register(r"FileBrowser", FileBrowserView)
router.register(r"WebDAV", WebDAVView)
router.register(r"FtpServer", FtpServerView)
router.register(r"KVStorage", KVStorageView)
router.register(r"Terminal", TerminalView)
router.register(r"IPTables", IPTablesView, basename="IPTables")
router.register(r"Crontab", CrontabViewSet)
router.register(r"DockerContainer", DockerContainerView, basename="DockerContainer")
router.register(r"DockerImage", DockerImageView, basename="DockerImage")
router.register(r"DockerVolume", DockerVolumeView, basename="DockerView")


admin.site.site_title = "UI-SSH"
admin.site.site_header = "UI-SSH"
urlpatterns = [
    path("", views.index, name="index"),
    path("api/version/", include("common.urls")),
    re_path(r"admin/", admin.site.urls),
    re_path(r"api/", include(router.urls)),
]

if settings.DEBUG:
    logging.debug("Additional debug routing configuration")

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
        # Optional UI:
        path(
            "docs/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "docs/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
        path("api-auth/", include("rest_framework.urls")),
        path("__debug__/", include(debug_toolbar.urls)),
    ]
