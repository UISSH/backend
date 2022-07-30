import sys
import uuid

from django.db import models
from loguru import logger

from base.dataclass import BaseOperatingRes

fmt = "{level} >>> {time:YYYY-MM-DD HH:mm:ss.SSS} | {function}:{line} - {message}"
logger.remove()
logger.add(sys.stderr, format=fmt)


class BaseModel(models.Model):
    create_at = models.DateTimeField(blank=True, auto_now_add=True, help_text="创建日期", verbose_name="创建日期")
    update_at = models.DateTimeField(blank=True, auto_now=True, help_text="更新日期", verbose_name="最后修改")

    class Meta:
        abstract = True

    @classmethod
    def log(cls, level="info", *args, **kwargs):

        if level == "info":
            logger.info(*args, **kwargs)
        elif level == "warning":
            logger.warning(*args, **kwargs)
        elif level == "critical":
            logger.critical(*args, **kwargs)
        elif level == 'error':
            logger.error(*args, **kwargs)
        else:
            logger.debug(*args, **kwargs)

    @classmethod
    def get_class_name(cls):
        return cls.__name__

    def update_new_value(self, **kwargs):
        """F
        如果字段有变动就更新

        :param kwargs:
        :return:
        """
        data = kwargs.pop("data", {})
        _data = vars(self)
        update_data = {}
        for i in data:
            # print(f"{_data[i]}=={data[i]}:{_data[i] == data[i]}")
            if _data[i] == data[i]:
                continue
            update_data[i] = data[i]

        if update_data:
            self.__dict__.update(update_data)
            self.save()
            return True
        return False

    @staticmethod
    def get_operating_res(event_id=None) -> BaseOperatingRes:
        if event_id is None:
            event_id = uuid.uuid4().__str__()
        instance: BaseOperatingRes = BaseOperatingRes.get_instance(event_id)
        if instance is None:
            instance = BaseOperatingRes(event_id=event_id)
        return instance
