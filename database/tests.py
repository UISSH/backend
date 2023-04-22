import os

from django.test import TestCase

from base.dataclass import BaseOperatingRes
from database.models.database_utils import (
    create_new_database,
    delete_database,
    export_backup_db,
    import_backup_db,
    update_password_database,
    update_username_database,
)


root_username = os.environ.get("DB_USERNAME", "root")
root_password = os.environ.get("DB_PASSWORD", "a.123456")


class TestDBDatabase(TestCase):
    def _pre_setup(self):
        super(TestDBDatabase, self)._pre_setup()
        self.db_name = f"test_db"
        self.db_password = f"test_password"
        self.db_old_username = f"test_old_username"
        self.db_new_username = f"test_new_username"

    def __create(self):
        op = BaseOperatingRes()
        create_new_database(
            op.event_id,
            self.db_name,
            self.db_old_username,
            self.db_password,
            root_username=root_username,
            root_password=root_password,
        )
        self.assertTrue(op.is_success())

    def __update_username(self):
        op = BaseOperatingRes()

        update_username_database(
            op.event_id,
            self.db_old_username,
            self.db_new_username,
            root_username=root_username,
            root_password=root_password,
        )
        self.assertTrue(op.is_success())

    def __update_password(self):
        op = BaseOperatingRes()
        update_password_database(
            op.event_id,
            self.db_new_username,
            "qwertyuiop1234567",
            root_username=root_username,
            root_password=root_password,
        )
        self.assertTrue(op.is_success())

    def __delete(self):
        op = BaseOperatingRes()

        delete_database(
            op.event_id,
            self.db_name,
            self.db_new_username,
            root_username=root_username,
            root_password=root_password,
        )
        self.assertTrue(op.is_success())

    def __export(self):
        op = BaseOperatingRes()
        export_backup_db(
            op.event_id,
            self.db_name,
            f"/tmp/{self.db_name}.sql",
            root_username=root_username,
            root_password=root_password,
        )
        # self.assertTrue(op.is_success())

    def __import(self):
        op = BaseOperatingRes()
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
