import datetime
import pathlib
import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pprint import pprint
from typing import List, Optional

from OpenSSL import crypto

from base.dataclass import BaseOperatingRes, BaseOperatingResEnum


class BackupTypeEnum(Enum):
    """
    - All
      Back up all data, when calling the 'recover' method, run normally in the same system environment.
    For example the following data：
      1. systemd config file
      2. ssl file
      3. website program
      4. website database
      ...
    - DATABASE
      MySQL, MariaDB or other DataBase data.
    - PROGRAM
      Website Program code etc.
    """
    All = 1
    DATABASE = 2
    PROGRAM = 3


OperatingResEnum = BaseOperatingResEnum


class SSLProvideEnum(Enum):
    LetsEncrypt = 1


class DataTypeEnum(Enum):
    MariaDB = 1
    MySQL = 2


class WebServerTypeEnum(Enum):
    Nginx = 1
    Apache = 2
    Lighttpd = 3
    IIS = 4
    Tomcat = 5
    Caddy = 6


class ApplicationStatusTypeEnum(Enum):
    OperatingStatus = 1
    BootStatus = 2


class ApplicationRunStatusEnum(Enum):
    Running = 1
    Stopped = 2


class ApplicationBootStatusEnum(Enum):
    Disable = 1
    Enable = 2


class BaseData(metaclass=ABCMeta):
    @abstractmethod
    def check_validity(self):
        pass

    @property
    def data(self) -> dict:
        """
          Verify the data, and return itself.__dict__ after the verification is passed.
          """
        self.check_validity()
        return self.__dict__

    @property
    def instance(self):
        """
        Verify the data, and return itself after the verification is passed.
        """
        self.check_validity()
        return self


@dataclass
class OperatingRes(BaseOperatingRes):
    pass


@dataclass
class SSLConfig:
    ssl_key_path: str
    ssl_certificate_path: str
    provide: SSLProvideEnum = SSLProvideEnum.LetsEncrypt


@dataclass
class BaseSSLCertificate:
    issued_common_name: str = ''

    issuer_common_name: str = ''
    issuer_country_name: str = ''
    issuer_organization_name: str = ''
    subject_alt_name: str = ''
    not_before: datetime.datetime = 0
    not_after: datetime.datetime = 0
    signature_algorithm: str = ''
    serial_number_hex: str = ''

    @classmethod
    def get_certificate(cls, certificate_path: str) -> "BaseSSLCertificate":
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(certificate_path).read())
        date_format, encoding = "%Y%m%d%H%M%SZ", "ascii"
        not_before = datetime.datetime.strptime(cert.get_notBefore().decode(encoding), date_format)
        not_after = datetime.datetime.strptime(cert.get_notAfter().decode(encoding), date_format)
        subject = cert.get_subject()
        issuer = cert.get_issuer()
        serial_number_hex = '{0:x}'.format(cert.get_serial_number())
        serial_number_hex = re.findall(".{2}", serial_number_hex.upper())
        serial_number_hex = ":".join(serial_number_hex)
        san = ''
        for i in range(0, cert.get_extension_count()):
            ext = cert.get_extension(i)
            if 'subjectAltName' in str(ext.get_short_name()):
                san = ext.__str__()
                continue

        return cls(subject.CN, issuer.CN, issuer.C, issuer.O, san, not_before, not_after,
                   cert.get_signature_algorithm().decode('utf-8'), serial_number_hex)

    def valid(self) -> bool:
        return self.not_before < datetime.datetime.now() < self.not_after

    def expire_after_days(self) -> int:
        return (self.not_after - datetime.datetime.now()).days


@dataclass
class ApplicationVersion:
    name: str
    author: str = ""
    website_url: str = ""
    docs_url: str = ""
    download_url: str = ""
    name_version: str = "1.0.0"
    code_version: int = "1"
    agreement_name: str = "Apache License 2.0"
    description: str = ""
    agreement_url: str = None


@dataclass
class DataBaseConfig:
    db_name: str
    username: str
    password: str
    db_type: DataTypeEnum = DataTypeEnum.MariaDB


@dataclass
class NewWebSiteConfig(BaseData):
    domain: str
    root_dir: str
    web_server_type: WebServerTypeEnum = WebServerTypeEnum.Nginx
    extra_domain: Optional[List[str]] = None
    ssl_config: Optional[SSLConfig] = None
    database_config: Optional[DataBaseConfig] = None
    web_server_config: str = None

    def check_validity(self):
        root_dir = pathlib.Path(self.root_dir)

        if not root_dir.exists():
            root_dir.mkdir(parents=True, exist_ok=True)
        if not root_dir.is_absolute():
            raise RuntimeError("The 'root_dir' attribute must be an absolute directory path.")
        if root_dir.is_file():
            raise RuntimeError("The 'root_dir' attribute value is file path , Expected is a directory path.")


if __name__ == '__main__':
    pprint(ApplicationRunStatusEnum(1))
    instance = BaseSSLCertificate.get_certificate('/etc/letsencrypt/live/ggdbacked.jcpumiao.com/fullchain.pem')
    pprint(instance.__dict__)
    print(instance.valid())
    print(instance.expire_after_days())
