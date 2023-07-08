from base.serializer import ICBaseSerializer
from rest_framework import serializers


class DockerVolumeSerializer(ICBaseSerializer):
    createdAt = serializers.CharField(label="CreatedAt")
    driver = serializers.CharField(label="Driver")
    labels = serializers.JSONField(label="Labels")
    mountpoint = serializers.CharField(label="Mountpoint")
    name = serializers.CharField(label="Name")
    options = serializers.JSONField(label="Options")
    scope = serializers.CharField(label="Scope")


class DockerVolumeDeleteSerializer(ICBaseSerializer):
    volumesDeleted = serializers.ListField(label="volumesDeleted")
    spaceReclaimed = serializers.IntegerField(label="spaceReclaimed")
