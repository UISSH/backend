"""
https://docker-py.readthedocs.io/en/stable/api.html
"""
import logging
from typing import Any, List

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

import docker
from base.viewset import BaseReadOnlyModelViewSet
from common.serializers.operating import OperatingResSerializer
from dockers.models.main import DockerContainerMode
from dockers.serializers.main import (
    DockerContainerListSerializer,
    DockerContainerModelSerializer,
    DockerContainerSerializer,
)


class DockerContainerView(BaseReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = DockerContainerMode.objects.all()
    serializer_class = DockerContainerModelSerializer
    client = None

    def __init__(self, **kwargs: Any) -> None:
        try:
            client = docker.APIClient(base_url="unix://var/run/docker.sock")
            if client.ping():
                self.client = client
        except Exception as e:
            logging.error("Docker is not running or not installed. detail: %s", e)
        super().__init__(**kwargs)

    @action(methods=["get"], detail=False, serializer_class=OperatingResSerializer)
    def ping(self, request, *args, **kwargs):
        """
        ping docker daemon with docker api.
        """
        op = OperatingResSerializer.get_operating_res()
        op.name = "ping docker daemon"
        try:
            if self.client.ping():
                op.msg = self.client.ping()
                op.set_success()
            else:
                op.set_failure("docker daemon is not running.")
            return Response(op.json())

        except Exception as e:
            op.set_failure("docker daemon is not running.")
            logging.error("Docker is not running or not installed. detail: %s", e)
        return Response(op.json())

    @action(
        methods=["get"],
        detail=False,
        serializer_class=DockerContainerListSerializer,
    )
    def list_docker_container(self, request, *args, **kwargs):
        """
        list docker container with docker api.
        """
        if self.client is None:
            msg = "docker daemon is not running."
            return Response(msg, status=500)

        return Response({"containers": self.client.containers(all=True)})
