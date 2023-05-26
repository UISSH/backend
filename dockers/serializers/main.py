from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from dockers.models.main import DockerContainerMode
from rest_framework import serializers


class DockerContainerModelSerializer(ICBaseModelSerializer):
    class Meta:
        model = DockerContainerMode
        fields = "__all__"


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
