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

import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView, SpectacularAPIView
from rest_framework.routers import DefaultRouter

from common.apis import user, opreating
from database.apis import database
from filebrowser.apis.filebrowser import FileBrowserView
from website.apis import website, application

router = DefaultRouter()
router.register(r'User', user.UserView)
router.register(r'OperatingRes', opreating.OperatingResView, basename="OperatingRes")
router.register(r'Website', website.WebsiteView)
router.register(r'Application', application.ApplicationView, basename="Application")
router.register(r"DataBase", database.DataBaseView)
router.register(r'Admin/User', user.AdminUserView)
router.register(r'FileBrowser', FileBrowserView)

admin.site.site_title = "GGDashboard"
admin.site.site_header = "GGDashboard"
urlpatterns = [
    path('websocket/', include('websocket.urls')),
    re_path(r'admin/', admin.site.urls),
    re_path(r'api/', include(router.urls))

]

if settings.DEBUG:
    from django.views import static

    print("附加 debug 路由配置")
    urlpatterns += [
        path('docs/schema/', SpectacularAPIView.as_view(), name='schema'),
        # Optional UI:
        path('docs/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('docs/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        path('api-auth/', include('rest_framework.urls')),
        path('__debug__/', include(debug_toolbar.urls)),

    ]
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', static.serve,
                {'document_root': settings.STATIC_ROOT}, name='static'),
    ]
