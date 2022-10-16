import os
import pathlib
import random
import string

import yaml

from website.applications.core.dataclass import NewWebSiteConfig

letters = string.ascii_letters + string.digits + string.punctuation.replace("'", '')


def random_str(length: 16):
    return ''.join(random.choice(letters) for _ in range(length))


def cmd(command: str, directory: pathlib.Path):
    os.system(f'cd {directory} && {command}')


def install_composer():
    target_bin = pathlib.Path('/usr/local/bin/composer')
    if target_bin.exists():
        return

    # https://getcomposer.org/download/
    install_script = """
    php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
    php -r "if (hash_file('sha384', 'composer-setup.php') === '55ce33d7678c5a611085589f1f3ddf8b3c52d662cd01d4ba75c0ee0459970c2200a51f492d557530c71c15d8dba01eae') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"
    php composer-setup.php
    php -r "unlink('composer-setup.php');"
    mv composer.phar /usr/local/bin/composer
    """
    return os.system(install_script)


def install_flarum(config: NewWebSiteConfig, app_config: dict):
    directory = pathlib.Path(config.root_dir)
    os.system(f'cd {directory.__str__()} && rm -rf * .*')
    cmd('composer create-project flarum/flarum . -n', directory)

    install_yaml_config = {"debug": False, "baseUrl": f"http://{config.domain}",
                           "databaseConfiguration": {"driver": "mysql", "host": "localhost", "port": 3306,
                                                     "database": config.database_config.db_name,
                                                     "username": config.database_config.username,
                                                     "password": config.database_config.password,
                                                     "prefix": False},
                           "adminUser": {"username": app_config.get('username'),
                                         "password": app_config.get('password'), "email": app_config.get('email')}}

    with open(pathlib.Path(config.root_dir) / 'config.yaml', 'w') as f:
        yaml.dump(install_yaml_config, f)

    cmd('php flarum install -f config.yaml', directory)
    os.system(f'chmod 775 -R {directory.absolute()}')
    os.system(f'chown -R www-data:www-data {directory.absolute()}')
