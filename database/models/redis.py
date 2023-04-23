import os
import pathlib
import uuid

from django.db import models
from django.db.models import IntegerChoices
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from base.base_model import BaseModel
from base.utils.logger import plog
from common.config import DB_SETTINGS
from common.models.User import User

from website.models import Website


def install_redis():
    pass


def upgrade_redis():
    pass


def uninstall_redis():
    pass


def backup_redis():
    pass


def restore_redis():
    pass


def start_redis():
    pass


def stop_redis():
    pass


def restart_redis():
    pass


def create_redis_instance(name):
    "/usr/local/uissh/data"
    redis_config = "/usr/local/uissh/redis"
    if not os.path.exists(redis_config):
        os.makedirs(redis_config)

    # open ../scripts/redis_example.conf and replace '[redis-name]' to uuid
    with open("/usr/local/uissh/backend/database/script/redis_example.conf", "r") as f:
        data = f.read()
        data = data.replace("[redis-name]", name)
    with open(f"{redis_config}/{name}.conf", "w") as f:
        f.write(data)

    # set workdir,pidfile,logfile,dbfilename

    # add to systemctl

    # enable redis-server service and start it


class RedisDB(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, unique=True)
    port = models.IntegerField(default=6379)
    protcol = models.CharField(max_length=255, default="tcp")
    host = models.CharField(max_length=255, default="127.0.0.1")
    default_db = models.BooleanField(default=False)


if __name__ == "__main__":
    create_redis_instance("test")
