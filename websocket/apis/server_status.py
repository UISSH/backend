import json
import logging
import time
import traceback
from threading import Thread
from typing import Optional

from channels.generic.websocket import WebsocketConsumer
from rest_framework.authtoken.models import Token

from base.utils.logger import plog
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
        super().__init__(*args, **kwargs)
        self.user: Optional[User] = None
        self.loop: Optional[Thread] = None
        self.stop = False
        self.cache = {}

    def monitoring_information(self, sql: str) -> None:
        start_time = time.time()
        run_count = 0
        max_run_count = 60 * 15
        while not self.stop:
            total_sec = 0
            msg = os_query_json(sql)
            self.send(
                text_data=json.dumps(
                    {
                        "doc": "https://osquery.io/schema/5.3.0/",
                        "action": "query",
                        "sql": sql,
                        "message": msg.__dict__,
                        "code": 200,
                    }
                )
            )
            while 1:
                interval = self.cache.get(sql)
                total_sec += 1
                if total_sec > interval or self.stop or run_count > max_run_count:
                    break
                time.sleep(1)
                run_count += 1

            if self.stop or run_count > max_run_count:
                break
        plog.info(
            f"monitoring_information thread is stop, cost {time.time() - start_time} seconds."
        )

    def connect(self):
        self.accept()
        token = self.scope["query_string"].decode("utf-8").split("=")[1]
        try:
            token = Token.objects.get(key=token)
            user = token.user
            if not user.is_superuser:
                self.send(
                    text_data=json.dumps({"message": "没有授权, 已终止本次会话.\r\n", "code": 403})
                )
                self.disconnect(403)
                return
        except Exception:
            plog.error("Failed to authenticate user with token")
            self.send(
                text_data=json.dumps({"message": "没有授权, 已终止本次会话.\r\n", "code": 403})
            )
            self.disconnect(403)
            return

        msg = "connection succeeded\r\n"
        try:
            self.send(text_data=json.dumps({"message": msg, "code": 201}))
        except Exception:
            plog.error("Failed to send message to client")
            self.disconnect(403)
            return

    def disconnect(self, close_code: int) -> None:
        logging.info("disconnect")
        self.stop = True

    def receive(self, text_data: str, bytes_data=None) -> None:
        text_data_json = json.loads(text_data)
        query_sql = text_data_json.get("query_sql")
        interval = text_data_json.get("interval", 5)
        interval = int(interval)
        if query_sql not in self.cache:
            self.cache[query_sql] = interval
            loop = Thread(target=self.monitoring_information, args=(query_sql,))
            loop.start()
            plog.debug(f"start new threading {loop.native_id}")
        else:
            self.cache[query_sql] = interval
