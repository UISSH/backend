from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from base.viewset import BaseModelViewSet
from webdav.models.webdav import WebDAVModel
from webdav.serializers.webdav import WebDAVModelSerializer, WebDAVPongSerializer
from webdav.utils import webdav


class WebDAVView(BaseModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = WebDAVModel.objects.all()
    serializer_class = WebDAVModelSerializer

    @action(methods=['get'], detail=False, serializer_class=WebDAVPongSerializer)
    def ping(self, request):
        return Response(WebDAVPongSerializer.get_data())

    @action(methods=['post'], detail=False, serializer_class=WebDAVPongSerializer)
    def install(self, request):

        webdav.install()
        return Response(WebDAVPongSerializer.get_data())

    @action(methods=['post'], detail=False, serializer_class=WebDAVPongSerializer)
    def reload_service(self, request):

        webdav.stop_service()
        webdav.start_service()
        return Response(WebDAVPongSerializer.get_data())

    @action(methods=['post'], detail=False, serializer_class=WebDAVPongSerializer)
    def start_service(self, request):

        webdav.start_service()
        return Response(WebDAVPongSerializer.get_data())

    @action(methods=['post'], detail=False, serializer_class=WebDAVPongSerializer)
    def stop_service(self, request):

        webdav.stop_service()
        return Response(WebDAVPongSerializer.get_data())

    def create(self, request, *args, **kwargs):
        res = super(WebDAVView, self).create(request, *args, **kwargs)
        if res.status_code == 201:
            WebDAVModel.sync_account()
        return res

    def update(self, request, *args, **kwargs):
        res = super(WebDAVView, self).update(request, *args, **kwargs)
        if res.status_code == 200:
            WebDAVModel.sync_account()
        return res

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True

        res = self.update(request, *args, **kwargs)
        if res.status_code == 200:
            WebDAVModel.sync_account()
        return res

    def destroy(self, request, *args, **kwargs):
        res = super(WebDAVView, self).destroy(request, *args, **kwargs)
        if res.status_code == 200:
            WebDAVModel.sync_account()
        return res
