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

from website.applications.core.application import Application, ApplicationToolMinx
from website.applications.core.dataclass import *
from .src.variable import app_parameter

abs_folder_path = pathlib.Path(__file__).parent.absolute()

with open(abs_folder_path / "home.html", "r") as f:
    html = f.read()

app_parameter = app_parameter


class NginxApplication(Application, ApplicationToolMinx):
    """ """

    def create(self):
        if self._config.web_server_type != WebServerTypeEnum.Nginx:
            raise RuntimeError(
                f"This app does not support {self._config.web_server_type.name} web server."
            )

        title = self._app_config.get("name", "default")
        text = self._app_config.get("text", "与君初相识，犹如故人归。嗨，别来无恙！<br>Hello World!")
        email = self._app_config.get("email", "")

        with open(f"{self._config.root_dir}/index.html", "w") as f:
            index_html = (
                html.replace("{title}", title)
                .replace("{domain}", self._config.domain)
                .replace("{text}", text)
            )
            if email:
                index_html = index_html.replace("{contact}", email)
            else:
                index_html = index_html.replace("{contact}", "")

            f.write(index_html)
        os.system(f"chown www-data.www-data -R {self._config.root_dir}")
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.SUCCESS)

    @classmethod
    def get_app_parameter(cls):
        return app_parameter

    def start(self):
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.SUCCESS)

    def stop(self):
        return OperatingRes(uuid.uuid4().hex, OperatingResEnum.SUCCESS)

    def read(self, *args, **kwargs) -> ApplicationWebServerConfig:
        nginx = """
    index index.html;
    location / {
        try_files $uri $uri/ =404;
    }
    """
        return ApplicationWebServerConfig(nginx)

    def delete(self, *args, **kwargs):
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
        name = "Nginx"
        return ApplicationVersion(
            name=name,
            name_version="0.0.1 alpha",
            code_version=1,
            author="zmaplex@gmail.com",
            description="用于创建基本的 Nginx 网页",
        )

    def get_data(self) -> dict:
        return self._storage.read()

    def size(self) -> int:
        return self._storage.size() + self.get_folder_size(self._config.root_dir)


if __name__ == "__main__":
    pass
