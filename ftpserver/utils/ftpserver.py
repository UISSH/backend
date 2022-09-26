import os
import pathlib

PROJECT_ROOT = '/usr/local/uissh'
FTP_SERVER_ROOT = f'{PROJECT_ROOT}/ftp-server'
FTP_SERVER_CONFIG = f'{FTP_SERVER_ROOT}/config.json'


def start_service():
    os.system('systemctl start ftp_server')


def stop_service():
    os.system('systemctl stop ftp_server')


def install():
    # remove folder that be old version created.
    os.system('systemctl stop ftp_server')
    os.system(f'rm -rf {PROJECT_ROOT}/ftpserver')

    # clean target folder
    os.system(f'rm -rf {FTP_SERVER_ROOT}')
    os.system('cd /usr/local/uissh/ && git clone https://github.com/UISSH/ftp-server.git')
    os.system(f'cd {FTP_SERVER_ROOT} && make && make install ')

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
