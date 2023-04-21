from rest_framework import permissions
from rest_framework.response import Response

from base.viewset import BaseModelViewSet
from common.models import KVStorage
from common.serializers.kv_storage import KVStorageSerializer


class KVStorageView(BaseModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = KVStorage.objects.all()
    serializer_class = KVStorageSerializer
    lookup_field = "key"
    search_fields = ["key"]

    def retrieve(self, request, *args, **kwargs):
        _key = self.kwargs["key"]
        KVStorage.objects.get_or_create(key=_key)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
