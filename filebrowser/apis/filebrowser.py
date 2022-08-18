import hashlib
import pathlib
import shlex
import subprocess

from django.db import models
from django.http import FileResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from base.dataclass import BaseOperatingRes
from base.utils.cache import IBaseCache
from base.utils.os_query import os_query_json
from base.utils.random_utils import random_str
from common.serializers.operating import OperatingResSerializer
from filebrowser.serializers.file import FileSerializer, UploadFileSerializer, ActionFileSerializer, UserSerializer, \
    TextOperatingSerializer


class VirtualFileModel(models.Model):
    """
    Interactive filesystem attributes and metadata.  https://osquery.io/schema/5.3.0/#file
    No corresponding table will actually be created, just to automatically generate documentation.
    """
    pass


class FileBrowserView(mixins.ListModelMixin,
                      GenericViewSet):
    permission_classes = (permissions.IsAdminUser,)
    queryset = VirtualFileModel.objects.none()
    serializer_class = FileSerializer
    pagination_class = None

    def get_queryset(self):
        return VirtualFileModel.objects.none()

    def list(self, request, *args, **kwargs):
        directory = request.query_params.get('directory', '/')
        data = os_query_json(f'SELECT * from file where directory="{directory}" order by "mtime" DESC ; ')

        serializer = FileSerializer(data=data.out, many=True)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)

    @action(methods=['get'], detail=False, serializer_class=UserSerializer)
    def get_users(self, request, *args, **kwargs):
        return Response(UserSerializer.get_users().data)

    @extend_schema(
        parameters=[OpenApiParameter(name="directory", allow_blank=True, default="/", description="directory"),
                    OpenApiParameter(name="path", allow_blank=True, description='absolute path')],
        responses=FileSerializer(many=True))
    @action(methods=['get'], detail=False)
    def query(self, request: Request, *args, **kwargs):
        if 'path' in request.query_params:
            path = request.query_params.get('path', '/')
            data = os_query_json(f'SELECT * from file where path="{path}" order by "type" ASC , "mtime" DESC;')

        else:
            directory = request.query_params.get('directory', '/')
            data = os_query_json(
                f'SELECT * from file where directory="{directory}" order by "type" ASC , "mtime" DESC;')

        serializer = FileSerializer(data=data.out, many=True)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)

    @extend_schema(parameters=[OpenApiParameter(name="path", description='absolute path')])
    @action(methods=['get'], detail=False)
    def request_download_file(self, request, *args, **kwargs):
        op = BaseOperatingRes()
        path = request.query_params.get('path', None)
        if path:
            _key = hashlib.md5(path.encode()).hexdigest()
            _cache = IBaseCache()
            token = random_str(128)
            _cache.set(_key, token)
            op.msg = token
            op.set_success()
            return Response(op.json())
        else:
            op.msg = "'path' parameter is required."
            op.set_failure()
            return Response(op.json(), status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(parameters=[OpenApiParameter(name="path", description='absolute path'),
                               OpenApiParameter(name="token", description='Download authorization')])
    @action(methods=['get'], detail=False, permission_classes=[permissions.AllowAny])
    def download_file(self, request, *args, **kwargs):
        path = request.query_params.get('path', None)
        token = request.query_params.get('token', None)
        if not path:
            return Response({'detail': "'path' parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        if token is None:
            return Response({'detail': "'token' parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        _cache = IBaseCache()
        _key = hashlib.md5(path.encode()).hexdigest()

        if _cache.get(_key, None) != token:
            return Response({'detail': f"invalid token."}, status=status.HTTP_404_NOT_FOUND)
        else:
            _cache.delete(_key)

        file = pathlib.Path(path)
        if not file.exists():
            return Response({'detail': f"'{path}' does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if file.is_dir():
            return Response({'detail': f"'{path}' is folder."}, status=status.HTTP_400_BAD_REQUEST)

        return FileResponse(file.open("rb"), as_attachment=True)

    @extend_schema(parameters=[OpenApiParameter(name="directory", description='directory')])
    @action(methods=['post'], detail=False, serializer_class=UploadFileSerializer)
    def upload_file(self, request: Request, *args, **kwargs):

        path = request.query_params.get('directory', None)
        if not path:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        file = request.FILES["file"]
        path = pathlib.Path(path)

        if not path.exists():
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        with open(path / file.name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        file = path / file.name

        return Response({"result": file.exists()})

    @extend_schema(responses=OperatingResSerializer)
    @action(methods=['post'], detail=False, serializer_class=ActionFileSerializer)
    def cmd(self, request: Request, *args, **kwargs):
        serializer = ActionFileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.save())

    @extend_schema(parameters=[OpenApiParameter(name="abs_path", description='file absolute path.')])
    @action(methods=['get', 'post'], detail=False, serializer_class=TextOperatingSerializer)
    def file_text_operating(self, request: Request, *args, **kwargs):
        file_path = request.query_params.get("abs_path", None)
        if file_path is None:
            return Response({'detail': f'`abs_path` parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        file_path = pathlib.Path(file_path)
        if not file_path.exists():
            return Response({'detail': f'{file_path} not found.'}, status=status.HTTP_404_NOT_FOUND)

        ret = subprocess.run(shlex.split(f'file -i {file_path.absolute()}'), capture_output=True)
        allow_list = ['inode/x-empty;', 'text/']

        allow = False
        for i in allow_list:
            if i in ret.stdout.decode():
                allow = True
                break
        # file < 1MB
        if file_path.stat().st_size < 1024 * 1024:
            allow = True

        if not allow:
            return Response({'detail': f'non text files are not supported.  {ret.stdout.decode()}'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        if request.method == "GET":
            with open(file_path, "r") as f:
                data = {'text': f.read(), 'path': f'{file_path}'}
            return Response(data)
        else:
            serializer = TextOperatingSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                return Response(serializer.save())
