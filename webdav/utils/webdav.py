import os
import pathlib
from functools import wraps

import nginxfmt
import yaml

PROJECT_ROOT = '/usr/local/uissh'
WEBDAV_CONFIG_YAML = f'{PROJECT_ROOT}/webdav/config.yaml'


def sync(config):
    def decorate(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if pathlib.Path(config).exists():
                with open(config, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f.read())

                kwargs['data'] = data
            else:
                print(f'"{config}" file does not exist.')
                return

            r = func(*args, **kwargs)
            data = yaml.safe_dump(data)
            with open(config, 'w') as f:
                f.write(data)
            return r

        return wrapper

    return decorate


@sync(WEBDAV_CONFIG_YAML)
def add_user(username, password, scope, data: dict = None):
    data['users'].append({'username': username,
                          "password": password,
                          "scope": scope
                          })


@sync(WEBDAV_CONFIG_YAML)
def del_user(username, password, scope, data: dict = None):
    data['users'].remove({'username': username,
                          "password": password,
                          "scope": scope
                          })


def start_service():
    os.system('systemctl start webdav_server')
    os.system('chown www-data.www-data /run/ui-ssh-webdav.socket')


def stop_service():
    os.system('systemctl stop webdav_server')


def download(version="v4.2.1"):
    os.system(f"mkdir {PROJECT_ROOT}/webdav")
    url = f"https://github.com/UISSH/webdav/releases/download/{version}/linux-amd64-webdav.tar.gz"
    os.system(f"wget {url} -O {PROJECT_ROOT}/webdav/linux-amd64-webdav.tar.gz ")
    os.system(f"cd {PROJECT_ROOT}/webdav/ && tar zxvf linux-amd64-webdav.tar.gz ")
    os.system("touch /run/ui-ssh-webdav.socket && chown www-data.www-data /run/ui-ssh-webdav.socket")
    os.system(f"cp {PROJECT_ROOT}/backend/webdav/utils/config.yaml {PROJECT_ROOT}/webdav/config.yaml")


def install_service():
    webdav_server_lib = '/lib/systemd/system/webdav_server.service'
    webdav_server_etc = '/etc/systemd/system/webdav_server.service'
    os.system(f'mv {PROJECT_ROOT}/backend/webdav/utils/webdav_server.sh {PROJECT_ROOT}/webdav/webdav_server.sh')
    os.system(f'chmod a+x {PROJECT_ROOT}/webdav/webdav_server.sh')
    os.system(f'cp  {PROJECT_ROOT}/backend/webdav/utils/webdav.service.example {webdav_server_lib}')
    os.system(f'rm -rf {webdav_server_etc}')
    os.system(f'ln -s  {webdav_server_lib}  {webdav_server_etc}')
    os.system('systemctl daemon-reload && systemctl enable webdav_server')


def append_server_nginx_config(data: str, new_config: str) -> str:
    """
    update nginx config.
    --------------------
    server {
        ...
        new_config will insert here.
    }
    --------------------
    """

    new_config = new_config + "}"
    f = nginxfmt.Formatter()
    data = data[::-1].replace("}", new_config[::-1], 1)[::-1]
    data = f.format_string(data)
    return data


def update_config():
    default_config = '/etc/nginx/sites-enabled/default'
    backend_ssl = '/etc/nginx/sites-enabled/backend_ssl.conf'
    webdav_config = f'{PROJECT_ROOT}/backend/webdav/utils/webdav_nginx.conf'
    with open(default_config, 'r') as f:
        default_config_data = f.read()
    with open(backend_ssl, 'r') as f:
        backend_ssl_data = f.read()
    with open(webdav_config, 'r') as f:
        webdav_config_data = f.read()

    if 'location /webdav' not in default_config_data:
        default_config_data = append_server_nginx_config(default_config_data, webdav_config_data)

    if 'location /webdav' not in backend_ssl_data:
        backend_ssl_data = append_server_nginx_config(backend_ssl_data, webdav_config_data)

    with open(default_config, 'w') as f:
        f.write(default_config_data)
    with open(backend_ssl, 'w') as f:
        f.write(backend_ssl_data)


def install():
    download()
    install_service()
    update_config()
    start_service()


def ping():
    """
    Determine whether it is installed and running.
    return (bool,bool)
    """
    installed = pathlib.Path(WEBDAV_CONFIG_YAML).exists()
    res = os.system('systemctl is-active --quiet webdav_server')
    status = res == 0
    return installed, status


if __name__ == '__main__':
    install()
