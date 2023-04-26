import logging
import pathlib
import uuid

from django.db import models
from django.db.models import IntegerChoices
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from base.base_model import BaseModel

from common.config import DB_SETTINGS
from common.models.User import User
from database.models.database_utils import (
    delete_database,
    update_password_database,
    update_username_database,
)
from website.models import Website


class DataBase(BaseModel):
    DATABASE_BACKUPS_DIR = "/var/db_backups"

    class DBType(IntegerChoices):
        MySQL = 0, "MySQL"
        MariaDB = 1, "MariaDB"

    class CreateStatus(IntegerChoices):
        PENDING = 0, "pending"
        SUCCESS = 1, "success"
        FAILED = 2, "failed"

    # ------------------------------------------constraint field-----------------------------------------#
    user = models.ForeignKey(
        User, verbose_name="user", blank=True, on_delete=models.CASCADE
    )
    website = models.OneToOneField(
        Website,
        default=None,
        null=True,
        blank=True,
        verbose_name="website",
        on_delete=models.SET_NULL,
    )
    # ---------------------------------------------------------------------------------------------------#

    name = models.CharField(
        verbose_name="Database name",
        unique=True,
        max_length=32,
        help_text="Once created, modification is not allowed, otherwise unforeseen bugs will occur.",
    )
    username = models.CharField(
        max_length=64, unique=True, verbose_name="Database username"
    )
    password = models.CharField(max_length=64, verbose_name="Database password")
    database_type = models.IntegerField(
        choices=DBType.choices, default=DBType.MariaDB, verbose_name="Database type"
    )

    character = models.CharField(
        max_length=32, default="utf8mb4", verbose_name="character"
    )
    collation = models.CharField(
        max_length=32, default="utf8mb4_general_ci", verbose_name="collation"
    )

    authorized_ip = models.CharField(
        max_length=64, default="localhost", verbose_name="authorized_ip"
    )

    create_status = models.IntegerField(
        default=CreateStatus.PENDING,
        choices=CreateStatus.choices,
        verbose_name="status",
        help_text="create database instance status",
    )

    class Meta:
        verbose_name = "DataBase"
        verbose_name_plural = "DataBases"

    def get_backup_dir(self) -> pathlib.Path:
        backup_dir = pathlib.Path(f"{self.DATABASE_BACKUPS_DIR}/{self.name}")
        return backup_dir

    def create_database_instance(self, event_id: str = uuid.uuid4().__str__()) -> str:
        from database.models.database_utils import create_new_database

        root_username = DB_SETTINGS.database_value()["database"]["root_username"]
        root_password = DB_SETTINGS.database_value()["database"]["root_password"]

        logging.debug("Create database instance.")
        create_new_database(
            event_id=event_id,
            name=self.name,
            username=self.username,
            password=self.password,
            character=self.character,
            collation=self.collation,
            authorized_ip=self.authorized_ip,
            root_username=root_username,
            root_password=root_password,
        )

        op_res = self.get_operating_res(event_id)
        logging.debug(f"Create database instance result: {op_res}")
        if op_res.is_success():
            backup_dir = self.get_backup_dir()
            if not backup_dir.exists():
                # https://stackoverflow.com/questions/6004073/how-can-i-create-directories-recursively
                backup_dir.mkdir(parents=True, exist_ok=True)
            self.create_status = self.CreateStatus.SUCCESS
            self.save()
        return event_id


@receiver(pre_save, sender=DataBase)
def pre_save_database_event(
    sender, instance: DataBase, raw, using, update_fields, **kwargs
):
    root_username = DB_SETTINGS.database_value()["database"]["root_username"]
    root_password = DB_SETTINGS.database_value()["database"]["root_password"]
    if not instance.id:
        # new create
        pass
    else:
        # update
        old_obj = DataBase.objects.get(id=instance.id)
        if (
            instance.username != old_obj.username
            or instance.authorized_ip != old_obj.authorized_ip
        ):
            logging.debug(
                "The database user name is modified and synchronized to the database."
            )
            op = instance.get_operating_res()
            update_username_database(
                op.event_id,
                old_obj.username,
                instance.username,
                authorized_ip=instance.authorized_ip,
                root_username=root_username,
                root_password=root_password,
            )

        if instance.password != old_obj.password:
            logging.debug(
                "The database user password is modified and synchronized to the database."
            )
            op = instance.get_operating_res()
            update_password_database(
                op.event_id,
                instance.username,
                instance.password,
                authorized_ip=instance.authorized_ip,
                root_username=root_username,
                root_password=root_password,
            )


@receiver(pre_delete, sender=DataBase)
def delete_database_event(sender, instance: DataBase, using, **kwargs):
    root_username = DB_SETTINGS.database_value()["database"]["root_username"]
    root_password = DB_SETTINGS.database_value()["database"]["root_password"]
    op = instance.get_operating_res()
    delete_database(
        op.event_id,
        name=instance.name,
        username=instance.username,
        authorized_ip=instance.authorized_ip,
        root_username=root_username,
        root_password=root_password,
    )
