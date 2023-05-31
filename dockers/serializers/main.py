import logging
from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from dockers.models.main import DockerContainerMode
from rest_framework import serializers


class DockerContainerModelSerializer(ICBaseModelSerializer):
    class Meta:
        model = DockerContainerMode
        fields = "__all__"


class CreateDockerContainerSerializer(ICBaseSerializer):
    name = serializers.CharField(max_length=255, label="name")
    image = serializers.CharField(
        max_length=255, label="image", help_text="nginx:latest"
    )
    port_bindings = serializers.JSONField(
        label="port_bindings", required=False, help_text="{80: 80, 443: 443}"
    )
    binds = serializers.JSONField(
        label="binds", required=False, help_text='{"/home/user1/": "/mnt/vol2"}'
    )
    environment = serializers.JSONField(
        label="environment", required=False, help_text='{"FOO": "BAR"}'
    )

    def create(self, validated_data):
        logging.info(f"create docker container: {validated_data}")
        return validated_data


class DockerContainerSerializer(ICBaseSerializer):
    command = serializers.CharField(max_length=255, label="command")
    created = serializers.IntegerField(label="created")
    host_config = serializers.JSONField(label="host_config")
    id = serializers.CharField(max_length=255, label="id")
    image = serializers.CharField(max_length=255, label="image")
    image_id = serializers.CharField(max_length=255, label="image_id")
    labels = serializers.JSONField(label="labels")
    mounts = serializers.JSONField(label="mounts")
    names = serializers.JSONField(label="names")
    network_settings = serializers.JSONField(label="network_settings")
    ports = serializers.JSONField(label="ports")
    state = serializers.CharField(max_length=255, label="state")
    status = serializers.CharField(max_length=255, label="status")


class DockerContainerListSerializer(ICBaseSerializer):
    containers = DockerContainerSerializer(many=True, label="containers")
