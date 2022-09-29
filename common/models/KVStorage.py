from django.db import models

from base.model import BaseModel


class KVStorage(BaseModel):
    key = models.CharField(max_length=128, verbose_name='key')
    value = models.CharField(max_length=102400, verbose_name='value')
