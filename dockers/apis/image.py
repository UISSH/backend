"""
https://docker-py.readthedocs.io/en/stable/api.html
"""
import logging
from typing import Any, List, Sequence
from drf_spectacular.utils import OpenApiParameter, extend_schema

import docker
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.serializers.operating import OperatingResSerializer
from dockers.serializers.image import (
    DockerImageInspectSerializer,
    DockerImageNameSerializer,
    DockerImageSerializer,
    SearchDockerImageListSerializer,
    SearchDockerImageSerializer,
)


def keys_lower(dict_data: dict):
    """transform dict keys first letter to lower case.

    for example:

    {
        'DockerImage':{
        "CreatedAt": "2021-08-04T08:10:00.000000000Z",
        }
    }

    to

    {
        'dockerImage':{
            "createdAt": "2021-08-04T08:10:00.000000000Z",
        }
    }

    """

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


def format_data(data: List[dict]) -> List[dict]:
    res = []
    for item in data:
        if isinstance(item, dict):
            res.append(keys_lower(item))

    return res


class DockerImageView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DockerImageSerializer
    client = None
    lookup_field = "image_id"

    def get_queryset(self):
        return []

    def get_lookup_content(self, request, *args, **kwargs):
        return request.parser_context["kwargs"][self.lookup_field]

    def __init__(self, **kwargs: Any) -> None:
        try:
            client = docker.APIClient(base_url="unix://var/run/docker.sock")
            if client.ping():
                self.client = client
        except Exception as e:
            logging.error("Docker is not running or not installed. detail: %s", e)
        super().__init__(**kwargs)

    @extend_schema(responses=OperatingResSerializer)
    @action(methods=["POST"], detail=False, serializer_class=DockerImageNameSerializer)
    def pull(self, request, *args, **kwargs):
        """
        pull docker image with docker api.
        #TODO async pull image
        """
        op = OperatingResSerializer.get_operating_res("pull image")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        op.set_processing()
        self.client.pull(data["name"])
        op.set_success()
        return Response(op.json(), status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        lookup_field = self.get_lookup_content(request)

        self.client.remove_image(image=lookup_field, force=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        lookup_field = self.get_lookup_content(request)
        data = self.client.images(all=True)
        for i in data:
            if lookup_field in i["Id"]:
                return Response(keys_lower(i))

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=["get"], detail=True, serializer_class=DockerImageInspectSerializer)
    def inspect(self, request, *args, **kwargs):
        lookup_field = self.get_lookup_content(request)
        data = self.client.inspect_image(lookup_field)
        return Response(keys_lower(data))

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                description="image name",
                type=str,
            )
        ],
    )
    @action(
        methods=["get"], detail=False, serializer_class=SearchDockerImageListSerializer
    )
    def search(self, request, *args, **kwargs):
        name = request.query_params.get("name", None)
        if name is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = self.client.search(name)

        return Response({"images": format_data(data)})

    def list(self, request, *args, **kwargs):
        """
        get docker container with docker api.
        """
        if self.client is None:
            msg = "docker daemon is not running."
            return Response(msg, status=500)
        data = self.client.images()

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
