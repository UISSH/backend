"""
https://docker-py.readthedocs.io/en/stable/api.html
"""

import logging
import os
import threading
from datetime import datetime, timedelta
from typing import Any, List

from django.http import FileResponse

import docker
import requests
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.serializers.operating import OperatingResSerializer
from dockers.serializers.main import (
    CreateDockerContainerSerializer,
    DockerContainerRestartPolicySerializer,
    DockerContainerSerializer,
    DockerInpectSerializer,
)

logging = logging.getLogger(__name__)


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

    @extend_schema(request=None)
    @action(methods=["post"], detail=False, serializer_class=OperatingResSerializer)
    def install(self, request, *args, **kwargs):
        """
        install docker
        """
        op = OperatingResSerializer.get_operating_res()
        op.name = "install docker"
        res = requests.get("https://ischina.org/")
        res_json = res.json()
        if res_json["is_china"]:
            command_text = """
            curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
            """
        else:
            command_text = """
            curl -fsSL https://get.docker.com | bash
            """

        def command():
            res = os.system(command_text)
            if res == 0:
                op.set_success()
            else:
                op.set_failure("install docker failed.")

        command_thread = threading.Thread(target=command)
        command_thread.start()

        return Response(op.json())

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

    @extend_schema(request=DockerContainerRestartPolicySerializer)
    @action(methods=["post"], detail=True, serializer_class=OperatingResSerializer)
    def set_restart_policy(self, request, *args, **kwargs):
        op = OperatingResSerializer.get_operating_res()
        lookup_field = request.parser_context["kwargs"]["docker_id"]

        policy_name = request.data["name"]
        maximum_retry_count = int(request.data["maximum_retry_count"])

        if policy_name != "on-failure":
            maximum_retry_count = 0

        self.client.update_container(
            lookup_field,
            restart_policy={
                "Name": request.data["name"],
                "MaximumRetryCount": maximum_retry_count,
            },
        )

        op.set_success()
        op.name = "set restart policy"
        op.msg = "set restart policy success."
        logging.info(request.data)
        return Response(op.json())

    @action(methods=["get"], detail=True, serializer_class=DockerInpectSerializer)
    def inspect(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        data = self.client.inspect_container(lookup_field)
        data = keys_lower(data)
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

    @action(methods=["get"], detail=True, serializer_class=OperatingResSerializer)
    def logs(self, request, *args, **kwargs):
        """show docker container logs in last 60 minutes."""
        op = OperatingResSerializer.get_operating_res()
        op.set_processing
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        since_time = datetime.now() - timedelta(minutes=60)
        data = self.client.logs(container=lookup_field, since=since_time.timestamp())
        op.msg = data
        op.set_success()
        return Response(op.json())

    @action(methods=["get"], detail=True, serializer_class=OperatingResSerializer)
    def donwloadLogs(self, request, *args, **kwargs):
        """download  docker container logs"""
        lookup_field = request.parser_context["kwargs"]["docker_id"]
        op = OperatingResSerializer.get_operating_res()
        op.name = "download docker container logs"
        op.set_processing()
        with open(f"/tmp/{lookup_field}.log", "wb") as f:
            f.write(self.client.logs(container=lookup_field))
        op.set_success()
        op.msg = f"/tmp/{lookup_field}.log"
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
                name=data.get("name", None),
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
