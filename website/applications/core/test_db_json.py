import time

from django.core.cache import cache
from django.test import TestCase

from website.applications.core.db_json import DBJson, DirectInitError
from website.models import ApplicationData


class TestDBJson(TestCase):
    def test_create(self):
        """_summary_
        test create
        """
        db_json = DBJson.get_instance("create")
        db_json["1"] = 1
        m = ApplicationData.objects.get(name="create")
        self.assertEqual(m.data, db_json)

    def test_update(self):
        """_summary_
        test update
        """
        db_json = DBJson.get_instance("update")
        db_json["1"] = 1
        m = ApplicationData.objects.get(name="update")
        self.assertEqual(m.data, db_json)
        db_json["1"] = 2
        db_json["2"] = "2"
        m.refresh_from_db()
        self.assertEqual(m.data, db_json)

    def test_delete_part(self):
        """_summary_
        test delete part
        """
        db_json = DBJson.get_instance("delete_part")
        db_json["1"] = 1
        db_json["2"] = "2"
        m = ApplicationData.objects.get(name="delete_part")
        self.assertEqual(m.data, db_json)
        item = db_json.pop("1")
        self.assertEqual(item, 1)
        m.refresh_from_db()
        self.assertEqual(m.data, db_json)

    def test_delete_all(self):
        """_summary_
        test delete all
        """
        db_json = DBJson.get_instance("delete_all")
        db_json["1"] = 1
        db_json["2"] = "2"
        m = ApplicationData.objects.get(name="delete_all")
        self.assertEqual(m.data, db_json)
        db_json.clear()
        m.refresh_from_db()
        self.assertEqual(m.data, db_json)

    def test_del_funcation(self):
        """_summary_
        test del funcation
        """
        db_json = DBJson.get_instance("del_funcation")
        db_json["1"] = 1
        db_json["2"] = "2"
        m = ApplicationData.objects.get(name="del_funcation")
        self.assertEqual(m.data, db_json)
        del db_json["1"]
        self.assertNotIn("1", db_json)
        m.refresh_from_db()
        self.assertEqual(m.data, db_json)

    def test_init(self):
        """_summary_
        test init
        """
        try:
            db_json = DBJson("init", {"1": 1})
        except Exception as e:
            self.assertIsInstance(e, DirectInitError)

    def test_gc(self):
        """_summary_
        test memory leak
        """
        db_json_list = []
        hash_key_list = []

        num = 100

        for i in range(num):
            db_json = DBJson.get_instance(f"gc_{i}")
            db_json["gc_text"] = i

            db_json_list.append(db_json)
            hash_key_list.append(f"gc_{i}")

        for i in range(num):
            res = ApplicationData.objects.filter(name=f"gc_{i}").exists()
            self.assertTrue(res)

        for item in db_json_list:
            item.destroy()

        for i in range(num):
            key = f"gc_{i}"
            res = ApplicationData.objects.filter(name=key)
            self.assertFalse(res.exists())

            cache_key = f"{DBJson.CACHE_PREFIX}{key}"
            res = cache.get(cache_key)
            self.assertIsNone(res)
