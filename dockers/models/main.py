import logging

from django.dispatch import receiver
import docker
from django.db import models
from django.db.models.signals import post_delete

from base.base_model import BaseModel
from website.models.website import WebsiteModel


class DockerContainerMode(BaseModel):
    website = models.ForeignKey(
        WebsiteModel,
        on_delete=models.CASCADE,
    )
    docker_id = models.CharField(
        max_length=64, unique=True, verbose_name="container ID"
    )

    docker_name = models.CharField(max_length=255, verbose_name="container name")

    def __str__(self):
        return self.docker_name


@receiver(post_delete, sender=DockerContainerMode)
def delete_docker_container(sender, instance, **kwargs):
    if instance.docker_id is not None:
        try:
            client = docker.APIClient(base_url="unix://var/run/docker.sock")
            client.remove_container(instance.docker_id, force=True)
        except Exception as e:
            logging.error("Docker is not running or not installed. detail: %s", e)
