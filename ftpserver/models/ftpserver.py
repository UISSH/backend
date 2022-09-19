import json

from base.base_model import BaseModel
from django.db import models

from ftpserver.utils.ftpserver import FTP_SERVER_CONFIG


def _get_default_params():
    return {"basePath": "/"}


class FtpServerModel(BaseModel):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    file_system = models.CharField(default='os', max_length=32)
    params = models.JSONField(default=_get_default_params())

    @staticmethod
    def sync_account():
        accesses = []
        for item in FtpServerModel.objects.all():
            data = {"user": item.username, "pass": item.password, "fs": item.file_system, "params": item.params}
            accesses.append(data)

        with open(f"{FTP_SERVER_CONFIG}", "r") as f:
            account_data = json.load(f)

        account_data['accesses'] = accesses
        with open(f"{FTP_SERVER_CONFIG}", "w") as f:
            json.dump(account_data, f)
