"""
 Copyright 2022 zmaplex@gmail.com
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import os
import uuid

from website.applications.app.flarum.src.core import install_composer, install_flarum
from website.applications.app.flarum.src.parameters import app_parameter
from website.applications.app.flarum.src.parameters import flarum_nginx_config
from website.applications.core.application import Application, ApplicationToolMinx
from website.applications.core.dataclass import *


class FlarumApplication(Application, ApplicationToolMinx):
    def create(self):
        if self._config.web_server_type != WebServerTypeEnum.Nginx:
            raise RuntimeError(
                f"This app does not support {self._config.web_server_type.name} web server."
            )

        # if not self._config.database_config:
        #     raise RuntimeError(f"Need to configure database.")

        if self._config.databases is None:
            raise RuntimeError(f"Need to configure database.")

        if (
            self._config.databases.mariadb is None
            and self._config.databases.mysqldb is None
        ):
            raise RuntimeError(f"Need to configure database.")

        install_composer()
        install_flarum(self._config, self._app_config)
        os.system(f"chown www-data.www-data -R {self._config.root_dir}")
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.SUCCESS)

    @classmethod
    def get_app_parameter(cls):
        return app_parameter

    def start(self):
        return OperatingRes(
            uuid.uuid4().hex,
            OperatingResEnum.NOT_SUPPORT,
            msg="This operation is not supported.",
        )

    def stop(self):
        return OperatingRes(
            uuid.uuid4().hex,
            OperatingResEnum.NOT_SUPPORT,
            msg="This operation is not supported.",
        )

    def read(self, *args, **kwargs) -> ApplicationWebServerConfig:
        config = ApplicationWebServerConfig(
            flarum_nginx_config.replace("{root_dir}", self._config.root_dir)
        )
        config.enter_folder_name = "public"
        dot_nginx_config = pathlib.Path(f"{self._config.root_dir}/.nginx.conf")
        if not dot_nginx_config.exists():
            dot_nginx_config.touch()
        return config

    def update(self, *args, **kwargs):
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.NOT_SUPPORT)

    def delete(self, *args, **kwargs):
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.NOT_SUPPORT)

    def reload(self, *args, **kwargs):
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.NOT_SUPPORT)

    def backup(
        self, backup_path: str = None, backup_type: BackupTypeEnum = BackupTypeEnum.All
    ):
        os.system(f"tar zcvf {backup_path} {self._config.root_dir}")
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.SUCCESS)

    def recover(
        self, path: str = None, backup_type: BackupTypeEnum = BackupTypeEnum.All
    ) -> OperatingRes:
        pass

    def migrate(self, old_code_version: int, new_code_version: int):
        pass

    @classmethod
    def version(cls) -> ApplicationVersion:
        name = "Flarum"
        return ApplicationVersion(
            name=name,
            name_version="0.0.1 alpha",
            code_version=1,
            author="zmaplex@gmail.com",
            description="Deploy Flarum program",
        )

    def get_data(self) -> dict:
        return self._storage.read()

    def size(self) -> int:
        return self._storage.size() + self.get_folder_size(self._config.root_dir)

    def toggle_ssl(self, toggle: bool):
        config_php = pathlib.Path(self._config.root_dir) / "config.php"
        with open(config_php, "r") as f:
            data = f.read()
        if toggle:
            data = data.replace(
                f"http://{self._config.domain}", f"https://{self._config.domain}"
            )
        else:
            data = data.replace(
                f"https://{self._config.domain}", f"http://{self._config.domain}"
            )
        with open(config_php, "w") as f:
            f.write(data)
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.SUCCESS)

    def update_domain(self, old_domain: str, new_domain: str) -> OperatingRes:
        if old_domain is None or new_domain is None:
            return OperatingRes(uuid.uuid4().hex, OperatingResEnum.SUCCESS)

        config_php = pathlib.Path(self._config.root_dir) / "config.php"
        with open(config_php, "r") as f:
            data = f.read()

        data = data.replace(f"{old_domain}", f"{new_domain}")
        with open(config_php, "w") as f:
            f.write(data)
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.SUCCESS)

    def get_boot_status(self) -> ApplicationBootStatusEnum:
        return ApplicationBootStatusEnum.Enable

    def get_requried_databases(self) -> list[DataBaseListEnum]:
        data = self.list_installed_dataBase()

        if DataBaseListEnum.MariaDB in data:
            return [DataBaseListEnum.MariaDB]

        if DataBaseListEnum.MySQL in data:
            return [DataBaseListEnum.MySQL]

        raise RuntimeError("No database installed.")

    def get_requried_ports(self) -> list[int]:
        return [80, 443]

    def get_boot_status(self) -> ApplicationBootStatusEnum:
        return ApplicationBootStatusEnum.Enable

    def get_run_status():
        pass


if __name__ == "__main__":
    pass
