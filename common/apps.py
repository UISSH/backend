import logging
import sys
from typing import List

from django.apps import AppConfig

from base.config import ABSDBConfig


class CommonConfig(AppConfig):
    name = "common"

    def ready(self):
        if "manage.py" in sys.argv and "runserver" not in sys.argv:
            return
        from .config import get_db_configs

        super(CommonConfig, self).ready()
        self.init_config(get_db_configs())

    @staticmethod
    def read_file(filepath):
        with open(filepath, "r") as f:
            return f.read()

    def log_msg(self, msg):
        logging.debug(f"{self.name}::{msg}")

    def init_config(self, items: List[ABSDBConfig]):
        try:
            for item in items:
                item.init_data(self.name)
        except:
            pass
