import json
import os
import pathlib

try:
    from django.conf import settings

    WEBSITE_ADDRESS = settings.WEBSITE_ADDRESS
except:
    WEBSITE_ADDRESS = "https://demo.uissh.com"

PROJECT_ROOT = "/usr/local/uissh"
FTP_SERVER_ROOT = f"{PROJECT_ROOT}/ftp-server"
FTP_SERVER_CONFIG = f"{FTP_SERVER_ROOT}/config.json"


def start_service():
    os.system("systemctl start ftp_server")


def stop_service():
    os.system("systemctl stop ftp_server")


def install():
    # remove folder that be old version created.
    os.system("systemctl stop ftp_server")
    os.system(f"rm -rf {PROJECT_ROOT}/ftpserver")

    # clean target folder
    os.system(f"rm -rf {FTP_SERVER_ROOT}")
    os.system(
        "cd /usr/local/uissh/ && git clone https://github.com/UISSH/ftp-server.git"
    )
    os.system(f"cd {FTP_SERVER_ROOT} && make && make install ")

    # try setup website ssl

    tls_config = {"server_cert": {"cert": "cert.pem", "key": "key.pem"}}

    if len(WEBSITE_ADDRESS) > 4 and "https:" in WEBSITE_ADDRESS:
        domain = WEBSITE_ADDRESS.replace("https://", "").replace("/", "")
        cert = pathlib.Path(f"/etc/letsencrypt/live/{domain}/fullchain.pem")
        privkey = pathlib.Path(f"/etc/letsencrypt/live/{domain}/privkey.pem")
        if cert.exists() and privkey.exists():
            tls_config = {
                "server_cert": {"cert": cert.__str__(), "key": privkey.__str__()}
            }
    file_fd = pathlib.Path(f"{FTP_SERVER_ROOT}/config.json")
    conf = json.loads(file_fd.read_text())
    conf["tls"] = tls_config
    file_fd.write_text(json.dumps(conf, indent=2))
    stop_service()
    start_service()


def ping():
    """
    Determine whether it is installed and running.
    return (bool,bool)
    """
    installed = pathlib.Path(FTP_SERVER_CONFIG).exists()
    status = os.system("systemctl is-active --quiet ftp_server") == 0
    return installed, status


if __name__ == "__main__":
    install()
