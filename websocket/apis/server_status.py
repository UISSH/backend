import json
import time
import traceback
from threading import Thread

from channels.generic.websocket import WebsocketConsumer
from rest_framework.authtoken.models import Token

from base.utils.os_query import os_query_json
from common.models import User


class ServerStatusConsumer(WebsocketConsumer):
    """
    {
        "query_sql":"select *, 'cpu_time' as _qtype from cpu_time ; select *,'net' as _qtype  from interface_details;",
        "interval":1
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user: User = None
        self.loop: Thread = None
        self.stop = False
        self.cache = {}

    def monitoring_information(self, sql):

        while not self.stop:
            total_sec = 0
            # interval = self.cache.get(sql)
            # print(f"execute {sql}, interval {interval}")
            msg = os_query_json(sql)
            self.send(text_data=json.dumps(
                {'doc': 'https://osquery.io/schema/5.3.0/', 'action': 'query', 'sql': sql, 'message': msg.__dict__,
                 'code': 200}))
            while 1:
                interval = self.cache.get(sql)
                total_sec += 1
                if total_sec > interval:
                    break
                time.sleep(1)
        print('线程结束')

    def connect(self):
        self.accept()
        token = self.scope["query_string"].decode("utf-8").split("=")[1]
        try:
            token = Token.objects.get(key=token)
            user = token.user
            if not user.is_superuser:
                self.send(text_data=json.dumps({'message': "没有授权, 已终止本次会话.\r\n", "code": 403}))
                self.disconnect(403)
                return
        except Exception:
            print(traceback.format_exc())
            self.send(text_data=json.dumps({'message': "没有授权, 已终止本次会话.\r\n", "code": 403}))
            self.disconnect(403)
            return

        msg = "connection succeeded\r\n"

        self.send(text_data=json.dumps({'message': msg, 'code': 201}))

    def disconnect(self, close_code):
        print("disconnect")
        self.stop = True

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        query_sql = text_data_json.get('query_sql')
        interval = text_data_json.get('interval', 5)
        interval = int(interval)
        if query_sql not in self.cache:
            self.cache[query_sql] = interval
            loop = Thread(target=self.monitoring_information, args=(query_sql,))
            loop.start()
            print(f"start new threading {loop.native_id}:{query_sql}")
        else:
            self.cache[query_sql] = interval
