import os
import pathlib

PROJECT_ROOT = '/usr/local/uissh'
FTP_SERVER_ROOT = f'{PROJECT_ROOT}/ftpserver'
FTP_SERVER_CONFIG = f'{FTP_SERVER_ROOT}/config.json'

def start_service():
    os.system('systemctl start ftp_server')


def stop_service():
    os.system('systemctl stop ftp_server')


def download(version="v0.11.0"):
    os.system(f"mkdir -p {FTP_SERVER_ROOT}")
    url = f"https://github.com/fclairamb/ftpserver/releases/download/{version}/ftpserver-linux-amd64"
    os.system(f"wget {url} -O {FTP_SERVER_ROOT}/ftpserver")
    os.system(f"chmod a+x  {FTP_SERVER_ROOT}/ftpserver")
    os.system(f'cd {FTP_SERVER_ROOT} && openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out cert.pem'
              f' -keyout key.pem -subj "/C=GB/ST=London/L=London/O=Global Security/OU=IT Department/CN=uissh.com"' )


def install_service():
    server_etc = "/etc/systemd/system/ftp_server.service"
    server_lib = "/lib/systemd/system/ftp_server.service"
    os.system(f'cp {PROJECT_ROOT}/backend/ftpserver/utils/ftpserver.service.example {server_lib}')
    os.system(f'cp {PROJECT_ROOT}/backend/ftpserver/utils/config.json {FTP_SERVER_ROOT}/config.json')
    os.system(f'rm -rf {server_etc}')
    os.system(f'ln -s  {server_lib}  {server_etc}')
    os.system('systemctl daemon-reload && systemctl enable ftp_server')


def install():
    download()
    install_service()
    start_service()


def ping():
    """
    Determine whether it is installed and running.
    return (bool,bool)
    """
    installed = pathlib.Path(FTP_SERVER_CONFIG).exists()
    status = os.system('systemctl is-active --quiet ftp_server') == 0
    return installed, status


if __name__ == '__main__':
    install()
