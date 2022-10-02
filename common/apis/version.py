from drf_spectacular.utils import extend_schema
from rest_framework import serializers, generics, permissions
from rest_framework.response import Response

import version


class VersionInfoSerializer(serializers.Serializer):
    backend_current_version = serializers.CharField(read_only=True, default=version.CURRENT_VERSION)
    require_frontend_minimum_version = serializers.CharField(read_only=True, default=version.FRONTED_MINIMUM_VERSION)


class ResultSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True, default="ok")


class VersionView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=VersionInfoSerializer)
    def get(request, *args, **kwargs):
        return Response({"backend_current_version": version.CURRENT_VERSION,
                         "require_frontend_minimum_version": version.FRONTED_MINIMUM_VERSION})


@extend_schema(responses=ResultSerializer)
class UpgradeFrontend(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        version.upgrade_front_project()
        return Response({'detail': 'ok'})
