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
from dockers.serializers.image import (
    DockerImageInspectSerializer,
    DockerImageNameSerializer,
    DockerImageSerializer,
)
from dockers.serializers.volume import DockerVolumeSerializer


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


def format_data(data: List[dict]) -> List[dict]:
    res = []
    for item in data:
        if isinstance(item, dict):
            res.append(keys_lower(item))

    return res


class DockerVolumeView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DockerVolumeSerializer
    client = None
    lookup_field = "volume_name"

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
        lookup_field = request.parser_context["kwargs"]["volume_name"]
        self.client.remove_volume(lookup_field)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        lookup_field = request.parser_context["kwargs"]["volume_name"]
        data = self.client.volumes()["Volumes"]
        print("lookup_field: ", lookup_field)
        for i in data:
            if lookup_field in i["Name"]:
                return Response(keys_lower(i))

        return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        """
        get docker container with docker api.
        """
        if self.client is None:
            msg = "docker daemon is not running."
            return Response(msg, status=500)
        data = self.client.volumes()["Volumes"]

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
