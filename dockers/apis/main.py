"""
https://docker-py.readthedocs.io/en/stable/api.html
"""
import logging
from typing import Any, List

import docker
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.serializers.operating import OperatingResSerializer
from dockers.serializers.main import (
    CreateDockerContainerSerializer,
    DockerContainerSerializer,
)


def keys_lower(dict_data: dict):
    def first_lower(string: str):
        return string[0].lower() + string[1:]

    res = dict()
    for key in dict_data.keys():
        if isinstance(dict_data[key], dict):
            res[first_lower(key)] = keys_lower(dict_data[key])
        elif isinstance(dict_data[key], list):
            res[first_lower(key)] = []
            for item in dict_data[key]:
                if isinstance(item, dict):
                    res[first_lower(key)].append(keys_lower(item))
                else:
                    res[first_lower(key)].append(item)
        else:
            res[first_lower(key)] = dict_data[key]
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
    serializer_class = DockerContainerSerializer
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

    def destroy(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]

        self.client.remove_container(container=lookup_field, force=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        data = self.client.containers(all=True, filters={"id": lookup_field})
        data = format_data(data)
        if len(data) > 0:
            return Response(data[0])
        return Response(data)

    @extend_schema(request=None, responses=OperatingResSerializer)
    @action(methods=["POST"], detail=True, serializer_class=OperatingResSerializer)
    def start(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        op = OperatingResSerializer.get_operating_res()
        op.name = "start docker container"
        try:
            self.client.start(container=lookup_field)
            op.set_success()
        except Exception as e:
            op.set_failure(str(e))
            return Response(op.json())
        return Response(op.json())

    @extend_schema(request=None, responses=OperatingResSerializer)
    @action(methods=["POST"], detail=True, serializer_class=OperatingResSerializer)
    def stop(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        op = OperatingResSerializer.get_operating_res()
        op.name = "stop docker container"
        try:
            self.client.stop(container=lookup_field)
            op.set_success()
        except Exception as e:
            op.set_failure(str(e))
            return Response(op.json())
        return Response(op.json())

    @extend_schema(request=None, responses=OperatingResSerializer)
    @action(methods=["POST"], detail=True, serializer_class=OperatingResSerializer)
    def restart(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        op = OperatingResSerializer.get_operating_res()
        op.name = "restart docker container"
        try:
            self.client.restart(container=lookup_field)
            op.set_success()
        except Exception as e:
            op.set_failure(str(e))
            return Response(op.json())
        return Response(op.json())

    @extend_schema(request=None, responses=OperatingResSerializer)
    @action(methods=["POST"], detail=True, serializer_class=OperatingResSerializer)
    def pause(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        op = OperatingResSerializer.get_operating_res()
        op.name = "pause docker container"
        try:
            self.client.pause(container=lookup_field)
            op.set_success()
        except Exception as e:
            op.set_failure(str(e))
            return Response(op.json())
        return Response(op.json())

    @extend_schema(request=None, responses=OperatingResSerializer)
    @action(methods=["POST"], detail=True, serializer_class=OperatingResSerializer)
    def unpause(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        op = OperatingResSerializer.get_operating_res()
        op.name = "unpause docker container"
        try:
            self.client.unpause(container=lookup_field)
            op.set_success()
        except Exception as e:
            op.set_failure(str(e))
            return Response(op.json())
        return Response(op.json())

    @extend_schema(request=None, responses=OperatingResSerializer)
    @action(methods=["POST"], detail=True, serializer_class=OperatingResSerializer)
    def kill(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        op = OperatingResSerializer.get_operating_res()
        op.name = "kill docker container"
        try:
            self.client.kill(container=lookup_field)
            op.set_success()
        except Exception as e:
            op.set_failure(str(e))
            return Response(op.json())
        return Response(op.json())

    @extend_schema(
        request=CreateDockerContainerSerializer, responses=OperatingResSerializer
    )
    @action(methods=["POST"], detail=False)
    def create_container(self, request, *args, **kwargs):
        """create docker container with docker api."""
        op = OperatingResSerializer.get_operating_res()
        op.name = "create docker container"
        data = request.data
        try:
            container = self.client.create_container(
                image=data["image"],
                name=data["name"],
                environment=data.get("environment", None),
                host_config=self.client.create_host_config(
                    port_bindings=data.get("port_bindings", None),
                    binds=data.get("binds", None),
                ),
            )
            container_id = container.get("Id", None)
            op.msg = container_id
            op.set_success()
        except Exception as e:
            op.set_failure(str(e))
            return Response(op.json())

        return Response(op.json())

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
