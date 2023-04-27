import logging
import pathlib
from uuid import uuid4

from django.db import models
from base.base_model import BaseModel
from crontab.utils import CronTab
from django.db.models.signals import post_delete
from django.dispatch import receiver


class CrontabModel(BaseModel):
    """
    - sync method:  in order to sync crontab job between database and system crontab.
        - 1.  read  system crontab job to database and merge.
        - 2.  write database crontab job to system crontab.
    """

    uuid = models.UUIDField(
        verbose_name="uuid", default=uuid4, editable=False, unique=True
    )
    schedule = models.CharField(
        verbose_name="schedule expressions",
        max_length=768,
        help_text="https://crontab.guru/examples.html",
    )
    command = models.CharField(verbose_name="command", max_length=768)

    shellscript = models.CharField(
        verbose_name="shellscript", max_length=10240, null=True, blank=True
    )

    class Meta:
        verbose_name = "Crontab"
        verbose_name_plural = "Crontab"

    def __str__(self):
        return f"{self.uuid}"

    @classmethod
    def sync(cls):
        # diff system crontab and database crontab
        system_crontab = CronTab().list()
        logging.debug(f"system crontab: {system_crontab}")
        database_crontab = cls.objects.all()
        for i in system_crontab:
            schedule, command = i.split("    ")
            schedule = schedule.strip()
            command = command.strip()

            if not cls.objects.filter(schedule=schedule, command=command).exists():
                cls(schedule=schedule, command=command).save()

        # sync database crontab to system crontab
        lastest_crontab = CronTab()
        database_crontab = cls.objects.all()
        for i in database_crontab:
            if i.shellscript:
                shellscript_folder = pathlib.Path("/usr/local/uissh/crontab")
                shellscript_sh = shellscript_folder / pathlib.Path(f"{i.uuid.hex}.sh")
                if not shellscript_folder.exists():
                    shellscript_folder.mkdir(parents=True, exist_ok=True)

                shellscript_sh.write_text(
                    f"#!/usr/bin/bash\n#{i.schedule}\n#{i.command}" + i.shellscript
                )
                shellscript_sh.chmod(0o755)
                i.command = f"{shellscript_sh}"
                i.save()
            lastest_crontab.add(i.schedule, i.command)

        lastest_crontab.save()


@receiver(post_delete, sender=CrontabModel)
def __delete(sender, instance: CrontabModel, using, **kwargs):
    lastest_crontab = CronTab()
    lastest_crontab.remove(instance.schedule, instance.command)
    lastest_crontab.save()
