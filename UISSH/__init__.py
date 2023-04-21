from __future__ import absolute_import, unicode_literals

from pathlib import PurePath

from decouple import AutoConfig

from .celery import app as celery_app

__all__ = ("celery_app",)

# Build paths inside the project like this: BASE_DIR.joinpath('some')
# `pathlib` is better than writing: dirname(dirname(dirname(__file__)))
BASE_DIR = PurePath(__file__).parent.parent
# Loading `.env` files
# See docs: https://gitlab.com/mkleehammer/autoconfig
config = AutoConfig(search_path=BASE_DIR.joinpath("config"))
