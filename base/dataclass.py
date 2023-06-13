import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Type

import logging

logger = logging.getLogger(__name__)

CACHE_NAME_SPACE = "GlobalOperationResCache"


ALL_KEYS = {}

try:
    from django.core.cache import caches, cache

    # 1 day
    _DEFAULT_TIMEOUT = 60 * 60 * 24
    _CACHE: cache = caches[CACHE_NAME_SPACE]
except:
    logger.warning("django.core.cache not found, use dict as cache")

    class Cache(dict):
        def set(self, k, v):
            self[k] = v

        def get(self, k, default):
            if k in self:
                return self[k]
            else:
                return default

    _CACHE: cache = Cache()


class BaseOperatingResEnum(Enum):
    PENDING = 0
    SUCCESS = 1
    FAILURE = 2
    PROCESSING = 3
    NOT_SUPPORT = 4


@dataclass
class BaseOperatingRes:
    event_id: str = uuid.uuid4().__str__()

    result: BaseOperatingResEnum = BaseOperatingResEnum.PENDING
    name: str = "default"
    msg: str = ""
    create_at: str = datetime.now().__str__()

    def __setattr__(self, key, value):
        if "event_id" in self.__dict__:
            event_id = self.__dict__["event_id"]
            obj = BaseOperatingRes.get_instance(event_id, self)
            obj.__dict__[key] = value
            _CACHE.set(event_id, obj, _DEFAULT_TIMEOUT)
            ALL_KEYS[event_id] = {"expire_at": time.time() + _DEFAULT_TIMEOUT}

        else:
            self.__dict__[key] = value
            event_id = self.__dict__["event_id"]
            _CACHE.set(event_id, self, _DEFAULT_TIMEOUT)
            ALL_KEYS[event_id] = {"expire_at": time.time() + _DEFAULT_TIMEOUT}

    def __getattribute__(self, name: str):
        skip = [
            "result_enum",
            "is_success",
            "json",
            "get_instance",
            "get_all_keys",
        ]
        if name.startswith("_") or name in skip or name.startswith("set_"):
            return object.__getattribute__(self, name)
        event_id = object.__getattribute__(self, "event_id")
        data: BaseOperatingRes = _CACHE.get(event_id, self)
        return data.__dict__[name]

    @classmethod
    def get_all_keys(cls):
        data = [x for x in ALL_KEYS.keys() if ALL_KEYS[x]["expire_at"] > time.time()]
        data.reverse()
        cache_data = []
        for x in data:
            if x not in ALL_KEYS:
                ALL_KEYS.pop(x)
            v = _CACHE.get(x, None)
            if v:
                cache_data.append(v)
        return cache_data

    @classmethod
    def get_instance(cls, event_id: str, default=None) -> "BaseOperatingRes":
        instance: BaseOperatingRes = _CACHE.get(event_id, default)
        return instance

    @staticmethod
    def result_enum() -> Type[BaseOperatingResEnum]:
        return BaseOperatingResEnum

    def is_success(self) -> bool:
        return self.result == BaseOperatingResEnum.SUCCESS

    def set_success(self):
        self.result = BaseOperatingResEnum.SUCCESS

    def set_failure(self, msg=None):
        if msg:
            self.msg = msg
        self.result = BaseOperatingResEnum.FAILURE

    def set_processing(self):
        self.result = BaseOperatingResEnum.PROCESSING

    def set_not_support(self):
        self.result = BaseOperatingResEnum.NOT_SUPPORT

    def json(self) -> dict:
        op = BaseOperatingRes.get_instance(self.event_id)
        data = op.__dict__
        result: Enum = op.__dict__["result"]
        data["result"] = {"result": result.value, "result_text": result.name}
        return data


@dataclass
class BaseOperatingResTest:
    event_id: str = uuid.uuid4().__str__()

    msg: str = ""
    result: BaseOperatingResEnum = BaseOperatingResEnum.PENDING
    create_at: str = datetime.now().__str__()

    def json(self):
        data = self.__dict__
        result: Enum = self.__dict__["result"]
        data["result"] = {"result": result.value, "result_text": result.name}
        return data


if __name__ == "__main__":
    print(BaseOperatingResTest().json())
    print(BaseOperatingRes().json())
