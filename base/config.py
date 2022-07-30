import abc

from django.db import models


class ABSDBConfig(object):
    __metaclass__ = abc.ABCMeta
    model: models.Model = models.Model

    def __init__(self, name, key, value):
        self._name = name
        self._key = key
        self._value = value

    def key(self):
        return self._key

    def name(self):
        return self._name

    def default_value(self):
        """
        :return:  返回默认值
        """
        return self._value

    @abc.abstractmethod
    def database_value(self):
        """
        有五秒缓存时间
        :return: 返回数据库记录的值
        """
        raise NotImplementedError('未实现该接口')

    @abc.abstractmethod
    def init_data(self, module_name):
        raise NotImplementedError('未实现该接口')

    def log_msg(self, msg):
        print(msg)

    def __str__(self):
        return f'{self._name}::{self._key}::{self._value}'
