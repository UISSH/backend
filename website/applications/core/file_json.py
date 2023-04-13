import json
import pathlib
import warnings


class FileJson(dict):
    """
    打开 JSON 文件，并返回该文件 FileJson 实例的引用
    TODO：由于读取文件会被缓存导致对象销毁时无法释放实例会造成内存泄露，需要修复。
    2023/04/12: 数据存储方式从文件变更为数据库，此类将被废弃

    """
    _CACHE = {}
    warnings.warn("FileJson is deprecated.")

    def __init__(self, path: str, data: dict = None):
        """
        Don't super().__init__()!
        """
        self.path = path
        if data is not None:
            self.update(data)
        self.__sync__()

    @classmethod
    def __get_file_json(cls, path):
        data = {}
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except:
            pass
        return data

    @classmethod
    def get_instance(cls, path: str) -> "FileJson":
        if path in cls._CACHE:
            instance = cls._CACHE[path]
        else:
            path = pathlib.Path(path)
            if path.exists():
                data = cls.__get_file_json(path.__str__())
                instance = cls(f'{path.absolute()}', data)
            else:
                path.touch()
                instance = cls(f'{path.absolute()}', {})
            cls._CACHE[path] = instance
        return instance

    def __sync__(self):

        with open(self.path, "w") as f:
            json.dump(self, f, indent=2)

    def __setitem__(self, *args, **kwargs):
        super().__setitem__(*args, **kwargs)
        self.__sync__()

    def update(self, E=None, **F):
        super().update(E, **F)
        self.__sync__()

    def __delitem__(self, *args, **kwargs):
        super().__delitem__(*args, **kwargs)
        self.__sync__()

    def pop(self, k, d=None):  # real signature unknown; restored from __doc__
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.

        If the key is not found, return the default if given; otherwise,
        raise a KeyError.
        """

        data = super().pop(k, d)
        self.__sync__()
        return data

    def popitem(self, *args, **kwargs):  # real signature unknown
        """
        Remove and return a (key, value) pair as a 2-tuple.

        Pairs are returned in LIFO (last-in, first-out) order.
        Raises KeyError if the dict is empty.
        """
        data = super().popitem(*args, **kwargs)
        self.__sync__()
        return data

    def clear(self):  # real signature unknown; restored from __doc__
        """ D.clear() -> None.  Remove all items from D. """
        super().clear()
        self.__sync__()

    def __call__(self, seq=None, **kwargs):
        data = {}

        if seq:
            data = dict(seq, **kwargs)

        if self.path in self._CACHE:
            instance = self._CACHE.get(self.path)
            instance.clear()
            instance.update(data)
            return instance
        else:
            self.clear()
            self.update(data)
            self._CACHE[self.path] = self
            return self

    def __del__(self):
        self.__sync__()

# a = FileJson('str')
#
# a = a({'init': 'init'})
#
# a.update({"update": 'update'})
#
# a = a({'sec': '2'})
