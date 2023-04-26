from django.test import TestCase

from website.applications.app_factory import AppFactory


class TestWordPress(TestCase):
    def test_get_application_module(self):
        app_factory = AppFactory
        app_factory.load()
        config = {}
        app_factory.get_application_module("WordPressApplication", config)
