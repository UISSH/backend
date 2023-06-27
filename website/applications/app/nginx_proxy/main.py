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


app_parameter = app_parameter


class NginxReverseProxyApplication(Application, ApplicationToolMinx):
    """
    https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
    """

    def create(self):
        if self._config.web_server_type != WebServerTypeEnum.Nginx:
            raise RuntimeError(
                f"This app does not support {self._config.web_server_type.name} web server."
            )

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
        proxy_pass = self._app_config.get("proxy_pass", "http://127.0.0.1:32768")
        nginx = f"""
    location / {{
        proxy_pass  {proxy_pass};
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   Host $host;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
    }}
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
        name = "NginxReverseProxy"
        return ApplicationVersion(
            name=name,
            name_version="0.0.1 alpha",
            code_version=1,
            author="zmaplex@gmail.com",
            description="When NGINX proxies a request, it sends the request to a specified proxied server, fetches the response, and sends it back to the client.",
        )

    def get_data(self) -> dict:
        return self._storage.read()

    def size(self) -> int:
        return self._storage.size() + self.get_folder_size(self._config.root_dir)

    def get_boot_status(self) -> ApplicationBootStatusEnum:
        return ApplicationBootStatusEnum.Enable

    def get_requried_databases(self) -> list[DataBaseListEnum]:
        return []

    def get_requried_ports(self) -> list[int]:
        return [80, 443]

    def get_run_status():
        pass


if __name__ == "__main__":
    pass
