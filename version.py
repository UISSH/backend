"""
https://semver.org/
"""
import os

CURRENT_VERSION = 'v0.0.3-alpha'
FRONTED_MINIMUM_VERSION = 'v0.0.3-alpha'
MIRROR_URL = 'https://mirror-cloudflare.uissh.com/'
FRONTEND_URL = f"{MIRROR_URL}https://github.com/UISSH/frontend/releases/download/{FRONTED_MINIMUM_VERSION}/django_spa.zip"

PROJECT_DIR = "/usr/local/uissh"
BACKEND_DIR = f"{PROJECT_DIR}/backend"


def cmd(command):
    os.system(command)


def upgrade_front_project():
    cmd(f'cd {BACKEND_DIR}/static && wget {FRONTEND_URL} -O "django_spa.zip" && rm -rf common spa')
    cmd(f'cd {BACKEND_DIR}/static && unzip django_spa.zip')
    cmd(f'cd {BACKEND_DIR}/static && mv spa common')
    cmd(f'cd {PROJECT_DIR} && rm -rf backend-release-* *.zip')
