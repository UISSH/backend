from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSetMixin
from rest_framework import serializers

from base.dataclass import BaseOperatingRes
from common.serializers.operating import (
    ExecuteCommandSyncSerializer,
    OperatingResSerializer,
    QueryOperatingResSerializer,
)


# class OperatingView(ViewSetMixin, views.APIView):
class OperatingView(GenericViewSet):
    """
    query time consuming operations.
    """

    serializer_class = OperatingResSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=OperatingResSerializer,
        parameters=[
            OpenApiParameter(
                name="event_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="event id",
                required=True,
            )
        ],
    )
    @action(
        methods=["get"],
        detail=False,
        serializer_class=QueryOperatingResSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def query(self, request):
        event_id = request.query_params.get("event_id")
        data = BaseOperatingRes.get_instance(event_id)
        if data is None:
            data = BaseOperatingRes(event_id=event_id)
            data.set_failure("The operating was not found.")
        else:
            data.set_success()
        data = {
            "event_id": event_id,
            "msg": data.msg,
            "result": data.result.value,
            "result_text": data.result.name,
        }

        return Response(data)

    @extend_schema(responses=OperatingResSerializer)
    @action(
        methods=["POST"],
        detail=False,
        serializer_class=ExecuteCommandSyncSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def excute_command_sync(self, request):
        serializer = ExecuteCommandSyncSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.save())

    @extend_schema(responses=OperatingResSerializer)
    @action(
        methods=["POST"],
        detail=False,
        serializer_class=QueryOperatingResSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def excute_command_async(self, request):
        pass
