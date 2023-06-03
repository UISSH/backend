from django.db import models
from django.db.models import IntegerChoices
from django.db.models.signals import post_save
from django.dispatch import receiver

from base.base_model import BaseModel
from common.models.User import User


class DemoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("user")


class DemoModel(BaseModel):
    class StatusType(IntegerChoices):
        """
        UNPAID   ："未支付"
        PAID     ："已支付"
        CANCELED ："被取消"
        REFUND   ："已退款"
        """

        UNPAID = 0, "未支付"
        PAID = 1, "已支付"
        CANCELED = 2, "被取消"
        REFUND = 3, "已退款"
        FINISHED = 4, "已完成"

    objects = DemoManager()
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    name = models.CharField(verbose_name="名称", max_length=768)
    status = models.IntegerField(
        choices=StatusType.choices, default=StatusType.UNPAID, verbose_name="支付状态"
    )

    class Meta:
        unique_together = ["user", "name"]
        verbose_name = "演示"
        verbose_name_plural = "演示"
