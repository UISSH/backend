from django.test import TestCase

from crontab.utils import CronTab


class TestCronTab(TestCase):
    def setUp(self):
        self.cron = CronTab()
