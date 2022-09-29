from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request

from base.viewset import BaseModelViewSet, BaseReadOnlyModelViewSet
from common.models import KVStorage
from common.serializers.kv_storage import KVStorageSerializer


class KVStorageView(BaseModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = KVStorage.objects.all()
    serializer_class = KVStorageSerializer
