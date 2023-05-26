from django.db import models
from django.db.models import IntegerChoices
from django.db.models.signals import post_save
from django.dispatch import receiver

from base.base_model import BaseModel
from common.models.User import User


class DockerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("user")


class DockerContainerMode(BaseModel):
    docker_id = models.CharField(max_length=255, verbose_name="容器ID")
    name = models.CharField(max_length=255, verbose_name="容器名称")
    image_id = models.CharField(max_length=255, verbose_name="镜像ID")
    image_name = models.CharField(max_length=255, verbose_name="镜像名称")

    class Meta:
        db_table = "docker_container"
