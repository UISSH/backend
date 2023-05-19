import os

# Don't add v prefix
CURRENT_VERSION = "0.2.3"
FRONTED_MINIMUM_VERSION = "0.2.4"
MIRROR_URL = "https://mirror-cloudflare.uissh.com/"
FRONTEND_URL = f"{MIRROR_URL}https://github.com/UISSH/react-frontend/releases/download/v{FRONTED_MINIMUM_VERSION}/django_spa.zip"

PROJECT_DIR = "/usr/local/uissh"
BACKEND_DIR = f"{PROJECT_DIR}/backend"
PYTHON_INTERPRETER = f"{BACKEND_DIR}/venv/bin/python"


def cmd(command, msg=None):
    if msg:
        print(msg)
    os.system(command)


def upgrade_backend_project(version=CURRENT_VERSION):
    cmd(f"cd {BACKEND_DIR} && git fetch && git checkout v{version}")
    cmd(f"cd {BACKEND_DIR} && venv/bin/pip install -r requirements.txt")
    cmd(f"{PYTHON_INTERPRETER} {BACKEND_DIR}/manage.py makemigrations --noinput")
    cmd(f"{PYTHON_INTERPRETER} {BACKEND_DIR}/manage.py migrate --noinput")
    cmd(f"{PYTHON_INTERPRETER} {BACKEND_DIR}/manage.py collectstatic --noinput")
    cmd("systemctl stop ui-ssh")
    cmd("systemctl start ui-ssh")


def upgrade_front_project():
    """
    Download frontend from github and replace the old one
    """
    cmd(
        f'cd {BACKEND_DIR}/static && wget -q {FRONTEND_URL} -O "django_spa.zip" && rm -rf common spa dist',
        "Download frontend",
    )
    cmd(
        f"cd {BACKEND_DIR}/static && unzip django_spa.zip > /dev/null", "Unzip frontend"
    )
    cmd(f"cd {BACKEND_DIR}/static && mv django_spa common")
    cmd(f"cd {PROJECT_DIR} && rm -rf backend-release-* *.zip", "Clean...")


if __name__ == "__main__":
    upgrade_backend_project()
    upgrade_front_project()
