import logging
from io import StringIO
import os

import paramiko


logger = logging.getLogger(__name__)

folder = "/usr/local/uissh/data"

private_key_path = f"{folder}/uissh_key.pem"


def mkdir_data():
    if not os.path.exists(folder):
        os.makedirs(folder)


def remove_ssh_key():
    data = []
    with open("/root/.ssh/authorized_keys", "r") as f:
        for line in f.readlines():
            if "by_uissh" in line:
                continue
            data.append(line)

    with open("/root/.ssh/authorized_keys", "w") as f:
        f.writelines(data)


def generate_ssh_key():
    """
    Generate ssh key, the public key will be added to the authorized_keys file.
    it will be used to connect to the local ssh service that only allow from localhost.
    """

    mkdir_data()

    with open("/root/.ssh/authorized_keys", "r") as f:
        old_data = f.read()

    private_key_path_exists = os.path.exists(private_key_path)

    flag = not private_key_path_exists

    flag = flag or "by_uissh" not in old_data

    if flag:
        logging.info("generate ssh key...")
        key = paramiko.RSAKey.generate(4096)
        pub = key.get_base64()
        key.write_private_key_file(private_key_path)
        append_data = f'from="127.0.0.1" ssh-rsa {pub} by_uissh\n\n'

        # remove old authorized_keys
        remove_ssh_key()

        with open("/root/.ssh/authorized_keys", "w") as f:
            f.write(append_data + old_data)

    return {
        "pkey": paramiko.RSAKey.from_private_key(open(private_key_path)),
        "username": "root",
        "hostname": "127.0.0.1",
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
