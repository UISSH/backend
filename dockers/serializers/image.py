from base.serializer import ICBaseSerializer
from rest_framework import serializers


class DockerImageNameSerializer(ICBaseSerializer):
    name = serializers.CharField(label="name")


class DockerImageSerializer(ICBaseSerializer):
    containers = serializers.IntegerField(label="containers")
    created = serializers.IntegerField(label="created")
    id = serializers.CharField(max_length=255, label="id")
    labels = serializers.JSONField(label="labels")
    parentid = serializers.CharField(max_length=255, label="parentid")
    repodigests = serializers.JSONField(label="repodigests")
    repotags = serializers.JSONField(label="repotags")
    sharedsize = serializers.IntegerField(label="sharedsize")
    size = serializers.IntegerField(label="size")
    virtualsize = serializers.IntegerField(label="virtualsize")


class DockerImageInspectSerializer(ICBaseSerializer):
    id = serializers.CharField()
    created = serializers.CharField()
    container = serializers.CharField()
    containerconfig = serializers.DictField()
    dockerversion = serializers.CharField()
    author = serializers.CharField()
    config = serializers.DictField()
    architecture = serializers.CharField()
    os = serializers.CharField()
    size = serializers.IntegerField()
    virtualsize = serializers.IntegerField()
    graphdriver = serializers.DictField()
    rootfs = serializers.DictField()
    metadata = serializers.DictField()
