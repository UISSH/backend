from base.config import ABSDBConfig


class DBConfig(ABSDBConfig):
    from common.models.Config import SystemConfigModel

    model = SystemConfigModel

    def init_data(self, module_name):
        obj, created = self.model.objects.get_or_create(key=self._key)

        if created or obj.name != self._name:
            self.log_msg(f"Create configuration items: {self._name}")
            obj.name = self._name
            obj.value = self._value
            obj.enable = True
            obj.module_name = module_name
            obj.save()
        else:
            self.log_msg(f"Skip creation: {self._name} : {obj}")
            pass

    def database_value(self):
        return self.model.get_value(self._key)

    def __init__(self, name, key, value):
        super().__init__(name, key, value)


"""
这里定义新的默认配置，如：
HOST_URL = DBConfig('域名', 'HOST', {'HOST_URL':'http://129.226.227.90:6006})
系统将会默认创建此条配置项
"""
# API_URL = DBConfig('API域名', 'API_HOST', {'HOST_URL': 'http://127.0.0.1:7000'})
# FRONT_URL = DBConfig('前端域名', 'FRONT_HOST', {'HOST_URL': 'http://127.0.0.1:7000'})

DB_SETTINGS = DBConfig(
    "Settings",
    "SETTINGS",
    {"database": {"root_username": "root", "root_password": "*-*-*root_password*-*-*"}},
)

VARS = vars()


def get_db_configs():
    data = []
    for item in VARS.values():
        if isinstance(item, DBConfig):
            data.append(item)
    return data
