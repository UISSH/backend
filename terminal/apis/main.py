import json
from collections import OrderedDict

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from base.viewset import BaseReadOnlyModelViewSet
from terminal.models import SFTPUploadModel
from terminal.serializers.main import SFTPUploadSerializer, UploadFileSerializer


class TerminalView(BaseReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SFTPUploadModel.objects.all()
    serializer_class = SFTPUploadSerializer

    @action(methods=['post'], detail=False, serializer_class=UploadFileSerializer)
    def upload_file(self, request: Request, *args, **kwargs):
        data = OrderedDict()
        data.update(request.data)

        data['auth'] = json.loads(data.get('auth'))
        serializer = UploadFileSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return Response(data)
