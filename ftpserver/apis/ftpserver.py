import logging
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from base.viewset import BaseModelViewSet
from ftpserver.models.ftpserver import FtpServerModel
from ftpserver.serializers.ftpserver import (
    FtpServerModelSerializer,
    FtpServerPongSerializer,
    EmptySerializer,
)
from ftpserver.utils import ftpserver


class FtpServerView(BaseModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = FtpServerModel.objects.all()
    serializer_class = FtpServerModelSerializer

    @extend_schema(responses=FtpServerPongSerializer)
    @action(
        methods=["get"],
        detail=False,
    )
    def ping(self, request):
        return Response(FtpServerPongSerializer.get_data())

    @extend_schema(responses=FtpServerPongSerializer)
    @action(methods=["post"], detail=False, serializer_class=EmptySerializer)
    def install(self, request):
        ftpserver.install()

        if len(self.queryset.all()) > 0:
            FtpServerModel.sync_account()
            ftpserver.stop_service()
            ftpserver.start_service()

        return Response(FtpServerPongSerializer.get_data())

    @extend_schema(responses=FtpServerPongSerializer)
    @action(methods=["post"], detail=False, serializer_class=EmptySerializer)
    def reload_service(self, request):
        ftpserver.stop_service()
        ftpserver.start_service()
        return Response(FtpServerPongSerializer.get_data())

    @extend_schema(responses=FtpServerPongSerializer)
    @action(methods=["post"], detail=False, serializer_class=EmptySerializer)
    def start_service(self, request):
        ftpserver.start_service()
        return Response(FtpServerPongSerializer.get_data())

    @extend_schema(responses=FtpServerPongSerializer)
    @action(methods=["post"], detail=False, serializer_class=EmptySerializer)
    def sync_account(self, request):
        FtpServerModel.sync_account()
        ftpserver.stop_service()
        ftpserver.start_service()
        return Response(FtpServerPongSerializer.get_data())

    @extend_schema(responses=FtpServerPongSerializer)
    @action(methods=["post"], detail=False, serializer_class=EmptySerializer)
    def stop_service(self, request):
        ftpserver.stop_service()
        return Response(FtpServerPongSerializer.get_data())

    def create(self, request, *args, **kwargs):
        res = super(FtpServerView, self).create(request, *args, **kwargs)
        if res.status_code == 201:
            FtpServerModel.sync_account()
        return res

    def update(self, request, *args, **kwargs):
        res = super(FtpServerView, self).update(request, *args, **kwargs)
        if res.status_code == 200:
            FtpServerModel.sync_account()
        return res

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        res = self.update(request, *args, **kwargs)
        if res.status_code == 200:
            FtpServerModel.sync_account()
        return res

    def destroy(self, request, *args, **kwargs):
        res = super(FtpServerView, self).destroy(request, *args, **kwargs)
        logging.debug(res.status_code)
        if res.status_code == 204:
            logging.debug(" FtpServerModel.sync_account()")
            FtpServerModel.sync_account()
        return res
