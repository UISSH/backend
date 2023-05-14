import importlib
import inspect
import os
import pathlib
import traceback
import logging


from website.applications.core.application import Application, Storage
from website.applications.core.dataclass import WebSiteConfig, WebServerTypeEnum

filepath = "website/applications/app"


class AppFactory:
    MODULES = {}

    @staticmethod
    def get_application_list():
        _m = {}
        for _key in AppFactory.MODULES:
            data = AppFactory.MODULES[_key]
            try:
                module: Application = data.pop("module")
                data["attr"] = module.get_app_parameter()
            except:
                logger.log("ERROR", traceback.format_exc())
                continue
            _m[_key] = data
        return _m

    @staticmethod
    def load():
        files = os.listdir(filepath)
        for fi in files:
            fi_d = os.path.join(filepath, fi)
            if os.path.isdir(fi_d) and os.path.exists(f"{fi_d}/main.py"):
                _module = fi_d.replace("/", ".") + ".main"
                try:
                    obj = importlib.import_module(_module)
                    for attr in obj.__dict__:
                        _obj = obj.__dict__[attr]
                        if not inspect.isclass(_obj):
                            continue
                        if not issubclass(_obj, Application):
                            continue

                        if (
                            _obj.__name__ == "Application"
                            and _obj.__module__
                            == "website.applications.core.application"
                        ):
                            continue
                        logging.debug(f"{_obj.__name__} Loaded.")
                        AppFactory.MODULES[_obj.__name__] = {
                            "module": _obj,
                            "info": _obj.version().__dict__,
                        }

                except Exception as e:
                    print(f"Failed to import plugin：{_module}")
                    print(traceback.format_exc())

        return AppFactory.MODULES

    @staticmethod
    def get_application(name) -> Application:
        return AppFactory.MODULES[name]

    @staticmethod
    def get_application_module(
        name,
        config: WebSiteConfig,
        app_config: dict = None,
        storage_cls: Storage = None,
    ) -> Application:
        if storage_cls is None:
            return AppFactory.MODULES[name]["module"](config, app_config)
        else:
            return AppFactory.MODULES[name]["module"](config, app_config, storage_cls)


if __name__ == "__main__":
    pass
