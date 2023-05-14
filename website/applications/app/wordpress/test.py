from django.test import TestCase

from website.applications.app_factory import AppFactory
from website.applications.core.dataclass import WebSiteConfig, WebServerTypeEnum


class TestWordPress(TestCase):
    def test_get_application_module(self):
        app_factory = AppFactory
        app_factory.load()
        config = WebSiteConfig(
            domain="test.uissh.com",
            root_dir="/tmp/test.uissh.com",
            web_server_type=WebServerTypeEnum.Nginx,
        )
        app_factory.get_application_module("WordPressApplication", config)
