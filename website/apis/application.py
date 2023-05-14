import os

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from base.utils.shell import LinuxShell
from base.viewset import BaseReadOnlyModelViewSet
from common.serializers.operating import OperatingResSerializer
from website.applications.app_factory import AppFactory
from website.applications.core.application import Application
from website.applications.core.dataclass import WebSiteConfig, WebServerTypeEnum
from website.models import WebsiteModel
from website.serializers.website import WebsiteModelSerializer


class ApplicationView(BaseReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    app_factory = AppFactory
    queryset = WebsiteModel.objects.all()
    serializer_class = WebsiteModelSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.app_factory.MODULES == {}:
            self.app_factory.load()

    def _get_app_instance(
        self, website: WebsiteModel, data: dict = None
    ) -> Application:
        name = website.application
        config = WebSiteConfig(
            domain=website.domain,
            root_dir=website.index_root,
            web_server_type=WebServerTypeEnum.Nginx,
        )

        app = self.app_factory.get_application_module(name, config, data)
        return app

    @action(methods=["get"], detail=False)
    def list_application(self, request, *args, **kwargs):
        self.app_factory.load()
        data = self.app_factory.get_application_list()
        return Response(data)

    @action(methods=["post"], detail=True, serializer_class=OperatingResSerializer)
    def app_create(self, request, *args, **kwargs):
        instance: WebsiteModel = self.get_object()

        # https://docs.djangoproject.com/en/4.2/ref/models/instances/#django.db.models.Model.refresh_from_db
        instance.refresh_from_db()

        # 4.Create application instance
        app_factory = AppFactory
        app_factory.load()
        app = app_factory.get_application_module(
            instance.application,
            instance.get_app_website_config(),
            instance.application_config,
        )
        res = app.create()
        if not res.is_success():
            err_msg = res.__str__()
            instance.status = instance.StatusType.ERROR
            instance.status_info = f"101:create application error. {err_msg}"

        instance.save()
        return Response(res.json())

    @action(methods=["get"], detail=True, serializer_class=OperatingResSerializer)
    def app_delete(self, request, *args, **kwargs):
        obj: WebsiteModel = self.get_object()
        app = self._get_app_instance(obj)
        data = app.delete()
        return Response(data.json())

    @action(methods=["get"], detail=True, serializer_class=OperatingResSerializer)
    def app_start(self, request, *args, **kwargs):
        obj: WebsiteModel = self.get_object()
        app = self._get_app_instance(obj)

        cmd = (
            f"ln -s /etc/nginx/sites-available/{obj.domain}.conf /etc/nginx/sites-enabled/{obj.domain}.conf"
            f" && systemctl reload nginx "
        )

        ret = LinuxShell(cmd)
        data = app.start()
        obj.status = obj.StatusType.VALID
        obj.save()
        return Response(data.json())

    @action(methods=["get"], detail=True, serializer_class=OperatingResSerializer)
    def app_stop(self, request, *args, **kwargs):
        obj: WebsiteModel = self.get_object()
        app = self._get_app_instance(obj)
        cmd = f"rm -rf  /etc/nginx/sites-enabled/{obj.domain}.conf && systemctl reload nginx"
        ret = LinuxShell(cmd)
        data = app.stop()
        obj.status = obj.StatusType.SUSPEND
        obj.save()
        return Response(data.json())
