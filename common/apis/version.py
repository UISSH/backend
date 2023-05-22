import pkg_resources
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, serializers
from rest_framework.response import Response

import upgrade


def get_github_last_version():
    import requests

    url = "https://api.github.com/repos/UISSH/backend/tags"
    res = requests.get(url)
    return res.json()[0]["name"]


LATEST_VERSION = get_github_last_version()


def can_updated():
    current_ver = pkg_resources.parse_version(upgrade.CURRENT_VERSION)
    latest_ver = pkg_resources.parse_version(LATEST_VERSION)
    return current_ver < latest_ver


class VersionInfoSerializer(serializers.Serializer):
    current_version = serializers.CharField(
        read_only=True, default=upgrade.CURRENT_VERSION
    )
    latest_version = serializers.CharField(read_only=True, default=LATEST_VERSION)
    can_updated = serializers.BooleanField(read_only=True, default=can_updated())


class ResultSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True, default="ok")


class VersionView(generics.RetrieveAPIView, generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=VersionInfoSerializer)
    def get(self, request, *args, **kwargs):
        return Response(
            {
                "current_version": "v" + upgrade.CURRENT_VERSION,
                "latest_version": LATEST_VERSION,
                "can_updated": can_updated(),
            }
        )

    def post(self, request, *args, **kwargs):
        if not can_updated():
            return Response({"detail": "already latest version"})
        try:
            upgrade.upgrade_front_project()
            upgrade.upgrade_backend_project(LATEST_VERSION)

            return Response({"detail": "ok"})
        except Exception as e:
            return Response({"detail": str(e)}, status=500)
