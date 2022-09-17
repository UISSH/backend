import hashlib
import json
import os.path
import sys

from website.applications.core.dataclass import *
from website.applications.core.file_json import FileJson


class Storage(metaclass=ABCMeta):

    @abstractmethod
    def read(self, *args, **kwargs):
        pass

    @abstractmethod
    def write(self, data: str, *args, **kwargs):
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @staticmethod
    def calc_text_hash(data: str) -> str:
        return hashlib.md5(data.encode(encoding="UTF-8")).hexdigest()


class LocalStorage(Storage):

    def __init__(self, unique, dir_path: pathlib.Path = pathlib.Path('local_storage')):

        if not dir_path.exists():
            dir_path.mkdir()

        self.file = dir_path / unique

    def read(self, *args, **kwargs) -> FileJson:
        data = FileJson.get_instance(self.file.__str__())
        return data

    def write(self, data: dict, *args, **kwargs):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def size(self) -> int:
        if self.file.exists():
            return os.path.getsize(self.file)
        else:
            return 0


class ApplicationToolMinx:

    def get_folder_size(self, path='.'):
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.get_folder_size(entry.path)
        return total


class ApplicationStorage:

    def __init__(self, config: NewWebSiteConfig, app_config: dict = None, storage_cls=LocalStorage):
        app_path = pathlib.Path(sys.modules[self.__module__].__file__).parent
        hash_key = storage_cls.calc_text_hash(f"{self.__class__.__name__.__str__()}{config.domain}{config.root_dir}")
        self._storage = storage_cls(hash_key, dir_path=app_path / 'data')

        if app_config is not None:
            self._app_config = app_config
            data = self._storage.read()
            if 'app_config' in data:
                data['app_config'].update(app_config)
            else:
                data['app_config'] = app_config

        else:
            data = self._storage.read()
            if 'app_config' in data:
                self._app_config = data['app_config']
            else:
                self._app_config = {}


class Application(ApplicationStorage, metaclass=ABCMeta):
    """
    - self._config
      web config
    - self.app_config
    - self.storage_cls
    - self._storage

    Note 1: By default a unique application data is identified by the 'config.domain' and 'config.root_dir'.
    Note 2: Global application data read and write is not provided, You can implement one yourself based on the
            Storage(in 'website/applications/core/application.py') abstract class.
            Example:
            app = AppName(config=NewWebSiteConfig(...),app_config={...},storage_cls=you_storage_class)
    """

    def __init__(self, config: NewWebSiteConfig, app_config: dict = None, storage_cls=LocalStorage):
        not_allow = [":", "/", " "]
        for i in not_allow:
            if i in config.domain:
                raise RuntimeError(f"Invalid parameter: {config.domain} include '{i}' char")

        self._config: NewWebSiteConfig = config.instance
        super().__init__(config, app_config, storage_cls)

    @classmethod
    @abstractmethod
    def get_app_parameter(cls) -> list[dict]:
        """
        Get the extra parameters of the app and pass them to the front end.
        app_parameter = [
            {
                "attr": {},
                "name": "name",
                "label": {
                    "default": "title",
                    "en-US": "title"
                },
                "required": True,
                "description": {
                    "default": "your website title",
                    "en-US": "your website title"
                }
            },
            ...
        ]

        name: An <input> element 'name' attr.
        label: A form with input fields for text.
        required: optional fields.
        description: description of use.
        """
        pass



    @abstractmethod
    def create(self) -> OperatingRes:
        """
        Only call once, create related resources such as:
          - create systemd service but don't start or enable it.
          - application private configuration files, you can use 'self.storage' to read and write private configuration
            data (the data format must be a dictionary).
            Note 1: By default a unique application data is identified by the 'config.domain' and 'config.root_dir'.
            Note 2: Global application data read and write is not provided, You can implement one yourself based on the
            Storage(in 'website/applications/core/application.py') abstract class.
        """
        pass

    @abstractmethod
    def read(self) -> str:
        """
        Returns the configuration file of the web server.
        """
        pass

    @abstractmethod
    def delete(self) -> OperatingRes:
        """
        Delete all data, include(application)
        """
        pass

    @abstractmethod
    def start(self) -> OperatingRes:
        """
        It is recommended to ues  systemd service to start your application.
        """
        pass

    @abstractmethod
    def stop(self) -> OperatingRes:
        """
        It is recommended to ues systemd service to stop your application.
        """
        pass

    @abstractmethod
    def backup(self, path: str = None, backup_type: BackupTypeEnum = BackupTypeEnum.All) -> OperatingRes:
        """
        Backup data to specified compressed file, the 'path' e.g: /www/backup/domain/data_format.tar.gz
        """
        pass

    @abstractmethod
    def recover(self, path: str = None, backup_type: BackupTypeEnum = BackupTypeEnum.All) -> OperatingRes:
        """
        Restore from backup file.
        """
        pass

    @classmethod
    @abstractmethod
    def version(cls) -> ApplicationVersion:
        """
        Returns plugin version information.
        """
        pass

    @abstractmethod
    def size(self) -> int:
        """
        Returns the instance data size, include database size, website folder size etc.
        """

    def status(self, status_type: ApplicationStatusTypeEnum) -> Enum:
        """
        Return to this application status.
        """
        data = self._storage.read()
        if status_type == ApplicationStatusTypeEnum.BootStatus:
            return ApplicationStatusTypeEnum(data["status"]["boot_startup"])
        else:
            return ApplicationRunStatusEnum(data["status"]["run_status"])
