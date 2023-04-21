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

from website.applications.app.wordpress.src.core import install_wordpress
from website.applications.app.wordpress.src.variable import app_parameter
from website.applications.core.application import Application, ApplicationToolMinx
from website.applications.core.dataclass import *

app_parameter = app_parameter


class WordPressApplication(Application, ApplicationToolMinx):
    def create(self):
        if self._config.web_server_type != WebServerTypeEnum.Nginx:
            raise RuntimeError(
                f"This app does not support {self._config.web_server_type.name} web server."
            )
        download_url = self._app_config.get(
            "wordpress", "https://wordpress.org/wordpress-6.2.zip"
        )

        install_wordpress(
            download_url,
            self._config.root_dir,
            self._config.database_config.db_name,
            self._config.database_config.username,
            self._config.database_config.password,
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
        nginx = """
    index  index.php;
    location / {
        try_files $uri $uri/ /index.php?$args;
    }
    
    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_pass  unix:/run/php/php-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include /etc/nginx/fastcgi_params;
    }
    """
        return ApplicationWebServerConfig(nginx)

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
        name = "WordPress"
        return ApplicationVersion(
            name=name,
            name_version="0.0.1 alpha",
            code_version=1,
            author="zmaplex@gmail.com",
            description="用于创建 WordPress 博客",
        )

    def get_data(self) -> dict:
        return self._storage.read()

    def size(self) -> int:
        return self._storage.size() + self.get_folder_size(self._config.root_dir)


if __name__ == "__main__":
    pass
