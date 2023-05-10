from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from base.dataclass import BaseOperatingRes
from base.viewset import BaseModelViewSet
from crontab.models.main import CrontabModel
from crontab.serializers.main import CrontabModelSerializer


class CrontabViewSet(BaseModelViewSet):
    queryset = CrontabModel.objects.all()
    serializer_class = CrontabModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.all()

    @action(detail=False, methods=["get"])
    def sync(self, request, *args, **kwargs):
        op = BaseOperatingRes(name="sync iptables")
        try:
            CrontabModel.sync()
            op.set_success()
        except Exception as e:
            msg = f"failed to sync iptables: {e}"
            op.set_failure(msg)
        return Response(op.json())
