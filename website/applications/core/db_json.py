import inspect
from typing import Dict, Optional
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from website.models import ApplicationData


class DirectInitError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DBJson(dict):
    """
    usage:
        db_json = DBJson.get_instance("hash_key")
        - add
            db_json["1"] = 1
            db_json["2"] = "2"
        - update
            db_json["1"] = 2
            db_json["2"] = "2"
        - delete
            db_json.pop("1")
        - clear
            db_json.clear()
        - del
            del db_json["1"]

    Don't use following methods:
        1. db_json = DBJson("hash_key", {"1": 1})
        2. db_json = DBJson.get_instance("hash_key")
           db_json = {"1": 1}
    """

    CACHE_PREFIX = "dbjson_"

    def __init__(self, hash_key: str, data: Optional[Dict] = None):
        self.hash_key = None

        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)

        if calframe[1][3] != "get_instance":
            raise DirectInitError(
                "Don't init DBJson directly! please use DBJson.get_instance()")

        self.hash_key = hash_key

        if data is not None:
            self.update(data)

    @classmethod
    def get_instance(cls, hash_key: str, timeout: int = DEFAULT_TIMEOUT) -> "DBJson":
        cache_key = f"{cls.CACHE_PREFIX}{hash_key}"
        instance = cache.get(cache_key)

        if not instance:
            obj, _ = ApplicationData.objects.get_or_create(name=hash_key)
            instance = cls(hash_key, data=obj.data)

            # 将实例缓存到 Django Cache 中
            cache.set(cache_key, instance, timeout)

        return instance

    def __setitem__(self, *args, **kwargs):
        super().__setitem__(*args, **kwargs)
        self.__sync__()

    def update(self, E=None, **F):
        super().update(E, **F)
        self.__sync__()

    def __delitem__(self, *args, **kwargs):
        super().__delitem__(*args, **kwargs)
        self.__sync__()

    def pop(self, k, d=None):
        """
        Remove specified key and return the corresponding value.

        If the key is not found, return the default if given;
        otherwise, raise a KeyError.
        """
        data = super().pop(k, d)
        self.__sync__()
        return data

    def popitem(self):
        """
        Remove and return a (key, value) pair as a 2-tuple.

        Pairs are returned in LIFO (last-in, first-out) order.
        Raises KeyError if the dict is empty.
        """
        data = super().popitem()
        self.__sync__()
        return data

    def clear(self):
        super().clear()
        self.__sync__()

    def destroy(self):
        """
        删除数据库中与此实例对应的记录，并从缓存中移除实例。
        """
        if self.hash_key:
            ApplicationData.objects.filter(name=self.hash_key).delete()
            cache.delete(f"{self.CACHE_PREFIX}{self.hash_key}")
            del self

    def __sync__(self):
        if hasattr(self, "hash_key") and self.hash_key:
            data, _ = ApplicationData.objects.get_or_create(name=self.hash_key)
            data.data = self
            data.save()

            # 更新缓存中的实例
            cache.set(f"{self.CACHE_PREFIX}{self.hash_key}", self)

    def __del__(self):
        self.__sync__()
