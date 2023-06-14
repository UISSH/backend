import time
import uuid
import warnings

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, serializers, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSetMixin

from base.dataclass import BaseOperatingRes
from common.serializers.operating import (
    ExecuteCommandAsyncSerializer,
    ExecuteCommandSyncSerializer,
    OperatingResSerializer,
    QueryOperatingResSerializer,
)

msg = """
import time
import uuid
import warnings

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, serializers, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSetMixin

from base.dataclass import BaseOperatingRes
from common.serializers.operating import (
    ExecuteCommandAsyncSerializer,
    ExecuteCommandSyncSerializer,
    OperatingResSerializer,
    QueryOperatingResSerializer,
)
"""


def random_long_text():
    return "a" * 10000


# class OperatingView(ViewSetMixin, views.APIView):
class OperatingView(GenericViewSet):
    """
    query time consuming operations.
    """

    serializer_class = OperatingResSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BaseOperatingRes.get_all_keys()

    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get("pk")
        data = BaseOperatingRes.get_instance(name)
        if data is None:
            data = BaseOperatingRes(name=name)
            data.set_failure("The operating was not found.")

        return Response(data.json())

    @action(methods=["GET"], detail=False, serializer_class=OperatingResSerializer)
    def generate_op(self, request, *args, **kwargs):
        """
        This function is only for testing.
        """
        for i in range(0, 10):
            op = BaseOperatingRes(event_id=uuid.uuid4(), msg=msg)
            if i % 2 == 0:
                op.set_success()
            elif i % 3 == 0:
                op.set_failure("error")
            elif i % 5 == 0:
                pass
            else:
                op.set_processing()
        return Response("ok")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for i in queryset:
            data.append(i.json())

        page = self.paginate_queryset(data)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
        msg = "This interface is deprecated. Please use the retrieve interface."
        warnings.warn(msg, FutureWarning)
        event_id = request.query_params.get("event_id")
        data = BaseOperatingRes.get_instance(event_id)
        if data is None:
            data = BaseOperatingRes(event_id=event_id)
            data.set_failure("The operating was not found.")
        else:
            data.set_success()

        return Response(data.json())

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
        serializer_class=ExecuteCommandAsyncSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def excute_command_async(self, request):
        serializer = ExecuteCommandAsyncSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.save())
