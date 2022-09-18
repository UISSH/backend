import pathlib

import yaml
from django.db import models

from base.base_model import BaseModel
from webdav.utils.webdav import WEBDAV_CONFIG_YAML


class WebDAVModel(BaseModel):
    username = models.CharField(max_length=32, verbose_name="username")
    password = models.CharField(max_length=32, verbose_name="password")
    scope = models.CharField(max_length=512, verbose_name="scope")

    @staticmethod
    def sync_account():
        config_file = pathlib.Path(WEBDAV_CONFIG_YAML)
        if not config_file.exists():
            return

        data = config_file.read_text(encoding='utf-8')
        data = yaml.safe_load(data)

        users = []

        for i in WebDAVModel.objects.all():
            users.append({'username': i.username,
                          "password": i.password,
                          "scope": i.scope
                          })
        data['users'] = users

        data =  yaml.safe_dump(data)

        config_file.write_text(data)