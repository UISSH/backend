import os
import pathlib
import random
import string

import requests

letters = string.ascii_letters + string.digits + string.punctuation.replace("'", "")


def random_str(length: 16):
    return "".join(random.choice(letters) for _ in range(length))


def install_wordpress(url, root_dir, db_name, db_username, db_password):
    download_url = url
    res = requests.get(download_url)
    with open(f"{root_dir}/wordpress.zip", "wb") as f:
        f.write(res.content)
    os.system(
        f"cd {root_dir} && unzip wordpress.zip > /dev/null && mv wordpress/* ./ && rm wordpress.zip "
    )
    res.raise_for_status()

    abs_folder_path = pathlib.Path(__file__).parent.parent.absolute()

    with open(abs_folder_path / "static/wp-config.php", "r") as f:
        wp_config = f.read()

    wp_config = wp_config.replace("database_name_here", db_name)
    wp_config = wp_config.replace("username_here", db_username)
    wp_config = wp_config.replace("password_here", db_password)

    for x in range(1, 9):
        wp_config = wp_config.replace(f"put your unique phrase here{x}", random_str(64))

    with open(f"{root_dir}/wp-config.php", "w") as f:
        f.write(wp_config)


if __name__ == "__main__":
    print(random_str(64))
