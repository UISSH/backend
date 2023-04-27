from django.db import models

from base.model import BaseModel


class KVStorageModel(BaseModel):
    key = models.CharField(unique=True, max_length=128, verbose_name="key")
    value = models.CharField(
        default=None, blank=True, null=True, max_length=102400, verbose_name="value"
    )
