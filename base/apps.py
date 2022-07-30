from typing import List

from django.apps import AppConfig

from common.config import ABSDBConfig


class BaseConfig(AppConfig):

    def ready(self):
        from common.config import get_db_configs
        items = get_db_configs()
        self.init_config(items)

    @staticmethod
    def read_file(filepath):
        with open(filepath, 'r') as f:
            return f.read()

    def log_msg(self, msg):
        print(f"{self.name}::{msg}")

    def init_config(self, items: List[ABSDBConfig]):
        try:
            for item in items:
                item.init_data(self.name)
        except:
            pass


VARS = vars()


def get_db_configs():
    data = []
    for item in VARS.values():
        if isinstance(item, ABSDBConfig):
            data.append(item)
    return data
