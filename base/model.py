from django.db import models


class BaseModel(models.Model):
    create_at = models.DateTimeField(auto_now_add=True, help_text="创建日期", verbose_name="创建日期")
    update_at = models.DateTimeField(auto_now=True, help_text="更新日期", verbose_name="最后修改")

    class Meta:
        abstract = True
