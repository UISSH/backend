from django.db import models
from django.db.models import IntegerChoices

from base.base_model import BaseModel


class SFTPUploadModel(BaseModel):
    class StatusType(IntegerChoices):
        PENDING = 0, "PENDING"
        SUCCESSFUL = 1, "SUCCESSFUL"
        FAILED = 2, "FAILED"

    username = models.CharField(max_length=64, verbose_name="ssh username")
    hostname = models.CharField(max_length=128, verbose_name="remote host")
    filename = models.CharField(verbose_name="file name", max_length=768)
    target_path = models.CharField(
        max_length=512, verbose_name="uploaded file path on the remote server"
    )
    status = models.IntegerField(
        choices=StatusType.choices, default=StatusType.PENDING, verbose_name="status"
    )
