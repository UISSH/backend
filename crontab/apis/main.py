from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from base.dataclass import BaseOperatingRes
from base.viewset import BaseModelViewSet
from crontab.models.main import CrontabModel
from crontab.serializers.main import CrontabModelSerializer
from rest_framework import status


class CrontabViewSet(BaseModelViewSet):
    queryset = CrontabModel.objects.all()
    serializer_class = CrontabModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        CrontabModel.sync()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance: CrontabModel = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        instance.remove_from_system_crontab()
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        instance.sync()
        return Response(serializer.data)

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
