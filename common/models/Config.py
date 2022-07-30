from django.core.cache import cache
from django.db import models

from base.model import BaseModel


class SystemConfig(BaseModel):
    name = models.CharField(max_length=64, verbose_name="配置项")
    key = models.CharField(unique=True, max_length=32, verbose_name="配置键")
    value = models.JSONField(max_length=40280, null=True, verbose_name="配置值")
    enable = models.BooleanField(default=False, verbose_name="启用")
    module_name = models.CharField(max_length=64, default="默认模块", verbose_name="所属模块")

    @staticmethod
    def get_value(key_value):
        """
        缓存，当字段不存在会自动创建，返回一个 需要填写字段{字段名}的内容
        :param key_value:配置项
        :return:数据结果
        """
        data = cache.get(key_value)
        default_value = {"error": f"没有找到相关配置，已自动生成一条记录，如果检查无误请填写字段 {key_value} 的内容"}
        if data is None:
            obj, created = SystemConfig.objects.get_or_create(key=key_value)
            data = obj.value
            if created:
                obj.value = default_value
                obj.save()
                raise AttributeError(default_value)

            if default_value == data:
                raise AttributeError(default_value)

            if not obj.enable:
                raise AttributeError(f"{key_value} 配置项没有被启用！")

            cache.set(key_value, data, SystemConfig.Config.CACHE_TIME)
        else:
            pass

        return data

    def __str__(self):

        return f'{self.name}'

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "系统配置"
        verbose_name_plural = "系统配置"

    class Config(object):
        HOST = 'HOST'
        ALIPAY_CALL = 'ALIPAY_CALL'
        CACHE_TIME = 30
