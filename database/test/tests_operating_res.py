from django.test import TestCase


class GlobalOperatingTests(TestCase):
    def test_object_consistent(self):
        """
        测试从缓存读取的对象等于缓存之前的对象.
        Tests that the object read from the cache is equal to the object before the cache.
        """
        from base.dataclass import BaseOperatingRes

        op = BaseOperatingRes()
        _op = BaseOperatingRes.get_instance(op.event_id)
        _op.msg = "update new msg"
        self.assertEqual(op, _op)

    def test_data_consistency_1(self):
        """
        当从缓存中读取到对象数据被修改时,测试原来的对象数据是否也被改变.

        When the object data is modified from the cache,
        test whether the original object data has also been modified.
        """
        from base.dataclass import BaseOperatingRes

        op = BaseOperatingRes()

        def _do(event_id: str):
            _op = BaseOperatingRes.get_instance(event_id)
            _op.msg = "ok"
            _op.result = _op.result_enum().SUCCESS

        _do(op.event_id)
        self.assertIs(op.result, op.result_enum().SUCCESS)

    def test_data_consistency_2(self):
        """
        当原来的对象数据被修改时,测试缓存对象数据是否也被改变.
        When the original object data is modified, test whether the cached object data is also changed.
        """
        from base.dataclass import BaseOperatingRes

        op = BaseOperatingRes(result=BaseOperatingRes.result_enum().PROCESSING)
        _op = BaseOperatingRes.get_instance(op.event_id)

        self.assertIs(_op.result, op.result_enum().PROCESSING)
        op.result = op.result_enum().SUCCESS
        self.assertIs(_op.result, op.result_enum().SUCCESS)
        self.assertEqual(op, _op)

    def test_data_consistency_3(self):
        from base.dataclass import BaseOperatingRes

        op = BaseOperatingRes()
        op.set_failure()
        _op = BaseOperatingRes.get_instance(op.event_id)
        self.assertEqual(op, _op)
