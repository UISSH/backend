from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework import views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from base.dataclass import BaseOperatingRes
from common.serializers.operating import OperatingResSerializer, QueryOperatingResSerializer


class OperatingResView(ViewSetMixin, views.APIView):
    """
    query time consuming operations.
    """
    serializer_class = OperatingResSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=OperatingResSerializer)
    @action(methods=['post'], detail=False, serializer_class=QueryOperatingResSerializer,
            permission_classes=[permissions.IsAuthenticated])
    def query(self, request):
        event_id = request.data.get("event_id")
        data = BaseOperatingRes.get_instance(event_id)
        if data is None:
            data = BaseOperatingRes(event_id=event_id, msg="The operating was not found.")
        data.set_success()
        data = {"event_id": event_id, "msg": data.msg,
                "result": data.result.value, "result_text": data.result.name}

        return Response(data)
