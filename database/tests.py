import os
import uuid

from django.test import TestCase

from base.dataclass import BaseOperatingRes
from database.models.database_utils import (
    create_new_database,
    delete_database,
    export_backup_db,
    get_database_password,
    get_database_username,
    import_backup_db,
    update_password_database,
    update_username_database,
)

root_username = get_database_username()
root_password = get_database_password()


class TestDBDatabase(TestCase):
    def _pre_setup(self):
        super(TestDBDatabase, self)._pre_setup()
        self.db_name = f"test_db"
        self.db_password = f"test_password"
        self.db_old_username = f"test_old_username"
        self.db_new_username = f"test_new_username"

    def __create(self):
        op = BaseOperatingRes(uuid.uuid4().hex)
        create_new_database(
            op.event_id,
            self.db_name,
            self.db_old_username,
            self.db_password,
            root_username=root_username,
            root_password=root_password,
        )
        self.assertTrue(op.is_success(), "Create database failed")

    def __update_username(self):
        op = BaseOperatingRes(uuid.uuid4().hex)

        update_username_database(
            op.event_id,
            self.db_old_username,
            self.db_new_username,
            root_username=root_username,
            root_password=root_password,
        )
        self.assertTrue(op.is_success())

    def __update_password(self):
        op = BaseOperatingRes(uuid.uuid4().hex)
        update_password_database(
            op.event_id,
            self.db_new_username,
            "qwertyuiop1234567",
            root_username=root_username,
            root_password=root_password,
        )
        self.assertTrue(op.is_success())

    def __delete(self):
        op = BaseOperatingRes(uuid.uuid4().hex)

        delete_database(
            op.event_id,
            self.db_name,
            self.db_new_username,
            root_username=root_username,
            root_password=root_password,
        )
        self.assertTrue(op.is_success())

    def __export(self):
        op = BaseOperatingRes(uuid.uuid4().hex)
        export_backup_db(
            op.event_id,
            self.db_name,
            f"/tmp/{self.db_name}.sql",
            root_username=root_username,
            root_password=root_password,
        )
        # self.assertTrue(op.is_success())

    def __import(self):
        op = BaseOperatingRes(uuid.uuid4().hex)
        import_backup_db(
            op.event_id,
            self.db_name,
            f"/tmp/{self.db_name}.sql",
            root_username=root_username,
            root_password=root_password,
        )
        # self.assertTrue(op.is_success())

    def test_1(self):
        self.__create()
        self.__export()
        self.__import()
        self.__update_username()
        self.__update_password()
        self.__delete()
