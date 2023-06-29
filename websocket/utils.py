import logging
from io import StringIO
import os

import paramiko


logger = logging.getLogger(__name__)

folder = "/usr/local/uissh/data"


def mkdir_data():
    if not os.path.exists(folder):
        os.makedirs(folder)


def generate_ssh_key():
    """
    Generate ssh key, the public key will be added to the authorized_keys file.
    it will be used to connect to the local ssh service that only allow from localhost.
    """

    with open("/root/.ssh/authorized_keys", "r") as f:
        old_data = f.read()

    if "by_uissh" not in old_data:
        logging.info("generate ssh key...")
        key = paramiko.RSAKey.generate(4096)
        pub = key.get_base64()
        key.write_private_key_file(f"{folder}/uissh.pem")
        append_data = f'from="127.0.0.1" ssh-rsa {pub} by_uissh\n\n'
        with open("/root/.ssh/authorized_keys", "w") as f:
            f.write(append_data + old_data)

    return {
        "pkey": paramiko.RSAKey.from_private_key(open(f"{folder}/uissh.pem")),
        "username": "root",
        "hostname": "localhost",
    }


def format_ssh_auth_data(_format):
    """{
    hostname: "127.0.0.1",
    port: "22",
    username: "root",
    password: "",
    private_key: "",
    private_key_password: ""}
    """
    private_key = _format.pop("private_key", None)
    private_key_password = _format.pop("private_key_password", None)

    if private_key:
        private_key = StringIO(private_key)
        if private_key_password:
            pkey = paramiko.RSAKey.from_private_key(
                private_key, password=private_key_password
            )
        else:
            pkey = paramiko.RSAKey.from_private_key(private_key)

        private_key.close()
        del _format["password"]
        auth_info = _format
        auth_info["pkey"] = pkey

    elif not _format.get("password", None):
        # If there is no password and certificate,
        # try to use the certificate file in the project root directory for testing.
        logging.warning("Use project root certificate.")
        pkey = paramiko.RSAKey.from_private_key(open("./test.pem"))
        auth_info = _format
        auth_info["pkey"] = pkey

    else:
        auth_info = _format
    return auth_info
