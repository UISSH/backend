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
    os.system("systemctl start ftp-server")


def stop_service():
    os.system("systemctl stop ftp-server")


def install():
    # remove folder that be old version created.
    os.system("systemctl stop ftp-server")
    os.system(f"rm -rf {PROJECT_ROOT}/ftpserver")

    # clean target folder
    os.system(f"rm -rf {FTP_SERVER_ROOT}")
    os.system(
        "cd /usr/local/uissh/ && git clone https://github.com/UISSH/ftp-server.git"
    )
    os.system(f"cd {FTP_SERVER_ROOT} && make && make install ")

    # try setup website ssl

    tls_config = {"server_cert": {"cert": "cert.pem", "key": "key.pem"}}

    nginx_config = pathlib.Path("/etc/nginx/sites-enabled/backend_ssl.conf")

    if nginx_config.exists():
        nginx_config_data = nginx_config.read_text()
        try:
            cert_path = (
                nginx_config_data.split("ssl_certificate")[1].split(";")[0].strip()
            )
            privkey_path = (
                nginx_config_data.split("ssl_certificate_key")[1].split(";")[0].strip()
            )
            cert = pathlib.Path(cert_path)
            privkey = pathlib.Path(privkey_path)
            if cert.exists() and privkey.exists():
                tls_config = {
                    "server_cert": {"cert": cert.__str__(), "key": privkey.__str__()}
                }

        except:
            cert_path = ""
            privkey_path = ""

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
    status = os.system("systemctl is-active --quiet ftp-server") == 0
    return installed, status


if __name__ == "__main__":
    install()
