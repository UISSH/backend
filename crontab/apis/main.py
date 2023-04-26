from rest_framework import permissions
from rest_framework.decorators import action

from base.demo.serializers.main import MainSerializer
from base.viewset import BaseReadOnlyModelViewSet
from common.models import User


class FileView(BaseReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = MainSerializer

    # 通过某个字段来获取具体的对象
    lookup_field = "username"

    @action(methods=["post"], detail=True, permission_classes=[permissions.AllowAny])
    def notify(self, request, *args, **kwargs):
        """ """
