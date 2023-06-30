import os
import sys
import requests

# Don't add v prefix
CURRENT_VERSION = "0.2.9"
FRONTED_MINIMUM_VERSION = "0.2.7"

resp = requests.get("https://ischina.org/")

MIRROR_URL = ""
if resp.json()["is_china"]:
    MIRROR_URL = "https://mirror-cloudflare.uissh.com/"
FRONTEND_URL = f"{MIRROR_URL}https://github.com/UISSH/react-frontend/releases/download/v{FRONTED_MINIMUM_VERSION}/django_spa.zip"

PROJECT_DIR = "/usr/local/uissh"
BACKEND_DIR = f"{PROJECT_DIR}/backend"
PYTHON_INTERPRETER = f"{BACKEND_DIR}/venv/bin/python"


def upgrade_backend_project(version=CURRENT_VERSION):
    # remove v prefix
    if version.startswith("v"):
        version = version.lstrip("v")

    # fork a new process to upgrade backend project
    pid = os.fork()
    if pid > 0:
        return

    shell_script = f"""
    cd {BACKEND_DIR} && cp db.sqlite3 /usr/local/uissh/db.sqlite3.bak
    cd {BACKEND_DIR} && git reset --hard HEAD && git fetch && git checkout v{version} -f
    cd {BACKEND_DIR} && venv/bin/pip install -r requirements.txt
    mv /usr/local/uissh/db.sqlite3.bak {BACKEND_DIR}/db.sqlite3
    {PYTHON_INTERPRETER} {BACKEND_DIR}/manage.py makemigrations --noinput
    {PYTHON_INTERPRETER} {BACKEND_DIR}/manage.py migrate --noinput
    {PYTHON_INTERPRETER} {BACKEND_DIR}/manage.py collectstatic --noinput
    systemctl restart ui-ssh
    """

    for line in shell_script.split("\n"):
        if line.strip():
            os.system(line)


def upgrade_front_project():
    """
    Download frontend from github and replace the old one
    """

    # fork a new process to upgrade backend project
    pid = os.fork()
    if pid > 0:
        return

    shell_script = f"""
    cd {BACKEND_DIR}/static && wget -q {FRONTEND_URL} -O "django_spa.zip" && rm -rf common spa dist
    cd {BACKEND_DIR}/static && unzip django_spa.zip > /dev/null
    cd {BACKEND_DIR}/static && mv django_spa common
    cd {PROJECT_DIR} && rm -rf backend-release-* *.zip
    """
    for line in shell_script.split("\n"):
        if line.strip():
            os.system(line)


if __name__ == "__main__":
    print("Upgrade script for UISSH")
    if len(sys.argv) > 1:
        if sys.argv[1] == "frontend":
            upgrade_front_project()
        elif sys.argv[1] == "backend":
            upgrade_backend_project()
        else:
            print("Error: Invalid argument")

    else:
        print("Error: Missing argument")
