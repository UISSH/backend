from django.core.cache import caches


class IBaseCache(object):
    """
    缓存的封装
    """

    cache = caches["default"]

    def __init__(self, name="default"):
        if not self.cache is caches[name]:
            self.cache = caches[name]

    def get_or_set(self, key, val, time_out=60):
        """
        如果缓存没有命中，则更新缓存
        :param key:
        :param val:
        :param time_out: 过期时间
        :return: val
        """
        return self.cache.get_or_set(key, val, time_out)

    def set(self, key: str, value: object, timeout: int = 60, version: str = None):
        """

        :param key:是一个字符串
        :param value:可以任何 picklable 形式的 Python 对象
        :param timeout:timeout 参数是可选的，默认为 CACHES 中相应后端的 timeout 参数。
               它是值存在缓存里的秒数。timeout 设置为 None 时将永久缓存。timeout 为0将不缓存值。
        :param version: ?
        :return: None
        """
        return self.cache.set(key, value, timeout=60, version=None)

    def get(self, key, default=None, version=None):
        """
        https://docs.djangoproject.com/zh-hans/4.0/topics/cache/#django.core.caches.cache.get
        :param key:是一个字符串
        :param default:如果对象不在缓存中，将返回指定的值
        :param version:?
        :return:
        """
        return self.cache.get(key, default, version)

    def delete(self, key, version=None):
        return self.cache.delete(key, version)
