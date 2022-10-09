import os

CURRENT_VERSION = '0.0.3-alpha'
FRONTED_MINIMUM_VERSION = '0.0.3-alpha'
MIRROR_URL = 'https://mirror-cloudflare.uissh.com/'
FRONTEND_URL = f"{MIRROR_URL}https://github.com/UISSH/frontend/releases/download/v{FRONTED_MINIMUM_VERSION}/django_spa.zip"

PROJECT_DIR = "/usr/local/uissh"
BACKEND_DIR = f"{PROJECT_DIR}/backend"
PYTHON_INTERPRETER = f'{BACKEND_DIR}/venv/bin/python'


def cmd(command):
    os.system(command)


def upgrade_backend_project():
    cmd(f'cd {BACKEND_DIR} && wget https://github.com/UISSH/backend/archive/refs/tags/v{CURRENT_VERSION}.zip')
    cmd(f'cd {BACKEND_DIR} && unzip v{CURRENT_VERSION}.zip')
    cmd(f'cd {BACKEND_DIR} && cp backend-{CURRENT_VERSION}/* ./ -r')
    cmd(f'cd {BACKEND_DIR} && rm  backend-{CURRENT_VERSION}  *.zip -rf')
    cmd(f'{PYTHON_INTERPRETER} {BACKEND_DIR}/manage.py makemigrations')
    cmd(f'{PYTHON_INTERPRETER} {BACKEND_DIR}/manage.py migrate')


def upgrade_front_project():
    cmd(f'cd {BACKEND_DIR}/static && wget {FRONTEND_URL} -O "django_spa.zip" && rm -rf common spa')
    cmd(f'cd {BACKEND_DIR}/static && unzip django_spa.zip')
    cmd(f'cd {BACKEND_DIR}/static && mv spa common')
    cmd(f'cd {PROJECT_DIR} && rm -rf backend-release-* *.zip')


if __name__ == '__main__':
    upgrade_backend_project()
    upgrade_front_project()
