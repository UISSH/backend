from django.test import TestCase

from crontab.utils import CronTab


class TestCronTab(TestCase):
    def setUp(self):
        self.cron = CronTab()

    def tearDown(self):
        del self.cron

    def test_add_cron(self):
        self.cron.add("*/5 * * * * /path/to/command")
        self.assertIn("*/5 * * * * /path/to/command", self.cron.crontab_context)

    def test_remove_cron_strict(self):
        self.cron.add("*/5 * * * * /path/to/command")
        self.cron.remove("*/5 * * * * /path/to/command", strict=True)
        self.assertNotIn("*/5 * * * * /path/to/command", self.cron.crontab_context)

    def test_remove_cron_not_strict(self):
        self.cron.add("*/5 * * * * /path/to/command")
        self.cron.add("*/2 * * * * /path/to/command")
        self.cron.remove("*/5 * * * *", strict=False)
        self.assertNotIn("*/5 * * * * /path/to/command", self.cron.crontab_context)
        self.assertIn("*/2 * * * * /path/to/command", self.cron.crontab_context)

    def test_save_cron(self):
        self.cron.add("*/5 * * * * /path/to/command")
        self.cron.save()
        self.assertIn("*/5 * * * * /path/to/command", self.cron._crontab_context)
        self.cron.remove("*/5 * * * * /path/to/command")
        self.cron.save()
