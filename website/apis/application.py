from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from base.viewset import BaseReadOnlyModelViewSet
from common.serializers.operating import OperatingResSerializer
from website.applications.app_factory import AppFactory
from website.applications.core.application import Application
from website.applications.core.dataclass import NewWebSiteConfig, WebServerTypeEnum
from website.models import Website
from website.serializers.website import WebsiteModelSerializer


class ApplicationView(BaseReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    app_factory = AppFactory
    queryset = Website.objects.all()
    serializer_class = WebsiteModelSerializer

    def _get_app_instance(self, website: Website, data: dict = None) -> Application:
        name = website.application
        config = NewWebSiteConfig(domain=website.domain, root_dir=website.index_root,
                                  web_server_type=WebServerTypeEnum.Nginx)

        app = self.app_factory.get_application_module(name, config, data)
        return app

    @action(methods=["get"], detail=False)
    def list_application(self, request, *args, **kwargs):
        self.app_factory.load()
        data = self.app_factory.get_application_list()
        return Response(data)

    @action(methods=['get'], detail=True, serializer_class=OperatingResSerializer)
    def upgrade_app(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        app = self._get_app_instance(obj)
        op_res = app.update()
        return Response(op_res.json())

    @action(methods=['get'], detail=True, serializer_class=OperatingResSerializer)
    def app_create(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        app = self._get_app_instance(obj)
        data = app.create()
        return Response(data.json())

    @action(methods=['get'], detail=True, serializer_class=OperatingResSerializer)
    def app_update(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        app = self._get_app_instance(obj)
        data = app.update()
        return Response(data.json())

    @action(methods=['get'], detail=True, serializer_class=OperatingResSerializer)
    def app_delete(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        app = self._get_app_instance(obj)
        data = app.delete()
        return Response(data.json())

    @action(methods=['get'], detail=True, serializer_class=OperatingResSerializer)
    def app_reload(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        app = self._get_app_instance(obj)
        data = app.reload()
        return Response(data.json())

    @action(methods=['get'], detail=True, serializer_class=OperatingResSerializer)
    def app_start(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        app = self._get_app_instance(obj)
        data = app.start()
        return Response(data.json())

    @action(methods=['get'], detail=True, serializer_class=OperatingResSerializer)
    def app_stop(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        app = self._get_app_instance(obj)
        data = app.stop()
        return Response(data.json())

    @action(methods=['get'], detail=True, serializer_class=OperatingResSerializer)
    def app_disable(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        app = self._get_app_instance(obj)
        data = app.disable()
        return Response(data.json())

    @action(methods=['get'], detail=True, serializer_class=OperatingResSerializer)
    def app_enable(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        app = self._get_app_instance(obj)
        data = app.enable()
        return Response(data.json())
