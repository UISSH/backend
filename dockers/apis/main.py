"""
https://docker-py.readthedocs.io/en/stable/api.html
"""
import logging
from typing import Any, List
from rest_framework import status

import docker
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.serializers.operating import OperatingResSerializer
from dockers.models.main import DockerContainerMode
from dockers.serializers.main import (
    DockerContainerListSerializer,
    DockerContainerModelSerializer,
    DockerContainerSerializer,
)


def keys_lower(dict_data: dict):
    res = dict()
    for key in dict_data.keys():
        if isinstance(dict_data[key], dict):
            res[key.lower()] = keys_lower(dict_data[key])
        elif isinstance(dict_data[key], list):
            res[key.lower()] = []
            for item in dict_data[key]:
                if isinstance(item, dict):
                    res[key.lower()].append(keys_lower(item))
                else:
                    res[key.lower()].append(item)
        else:
            res[key.lower()] = dict_data[key]
    return res


# 重新格式化数据
def format_data(data: List[dict]) -> List[dict]:
    res = []
    for item in data:
        if isinstance(item, dict):
            res.append(keys_lower(item))

    return res


class DockerContainerView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DockerContainerListSerializer
    client = None
    lookup_field = "docker_id"

    def get_queryset(self):
        return []

    def __init__(self, **kwargs: Any) -> None:
        try:
            client = docker.APIClient(base_url="unix://var/run/docker.sock")
            if client.ping():
                self.client = client
        except Exception as e:
            logging.error("Docker is not running or not installed. detail: %s", e)
        super().__init__(**kwargs)

    def destroy(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]

        self.client.remove_container(container=lookup_field, force=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        data = self.client.containers(all=True, filters={"id": lookup_field})
        return Response(format_data(data))

    def list(self, request, *args, **kwargs):
        """
        get docker container with docker api.
        """
        if self.client is None:
            msg = "docker daemon is not running."
            return Response(msg, status=500)
        data = self.client.containers(all=True)

        return Response(
            {
                "pagination": {
                    "total": len(data),
                    "page": 1,
                    "pageSize": len(data),
                    "next": None,
                    "previous": None,
                },
                "results": format_data(data),
            }
        )

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
