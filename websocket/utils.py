import logging
from io import StringIO

import paramiko


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
