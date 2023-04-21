from django.db import models

from base.base_model import BaseModel


class ApplicationData(BaseModel):
    name = models.CharField(max_length=64, unique=True, verbose_name="名称")
    data = models.JSONField(verbose_name="数据", null=True, blank=True)

    class Meta:
        verbose_name = "应用数据"
        verbose_name_plural = "应用数据"

    def __str__(self):
        return self.name
