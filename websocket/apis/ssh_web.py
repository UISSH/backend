import json
import traceback
from threading import Thread
from typing import Optional

import paramiko
from channels.generic.websocket import WebsocketConsumer
from paramiko.channel import Channel
from rest_framework.authtoken.models import Token

from base.utils.logger import plog
from common.models import User
from websocket.utils import format_ssh_auth_data


class SshWebConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user: Optional[User] = None
        self.client: Optional[paramiko.SSHClient] = None
        self.ssh_session: Optional[Channel] = None
        self.connect_status = False
        self.loop: Optional[Thread] = None
        self.suspended_interactive = False
        self.current_work_dir = '/'

    def ssh_recv(self):
        while 1:
            if self.suspended_interactive:
                continue
            if self.connect_status is False:
                plog.debug("ssh_recv and websocket is closed.")
                self.loop = None
                break
            if self.ssh_session.recv_ready() is True:
                # it is Non blocking.
                msg = self.ssh_session.recv(2048)
                self.send(text_data=json.dumps({'message': msg.decode("utf-8"), 'code': 200}))
        print("terminal thread is ended.")

    def connect(self):
        self.accept()
        token = self.scope["query_string"].decode("utf-8").split("=")[1]
        try:
            token = Token.objects.get(key=token)
            user = token.user
            if not user.is_superuser:
                self.send(text_data=json.dumps(
                    {'message': "No authorization, this session has been terminated.\r\n", "code": 403}))
                self.disconnect(403)
                return
        except Exception:
            print(traceback.format_exc())
            self.send(text_data=json.dumps(
                {'message': "No authorization, this session has been terminated.\r\n", "code": 403}))
            self.disconnect(403)
            return
        self.connect_status = True

    def disconnect(self, close_code):
        room_name = self.scope['url_route']['kwargs']['room_name']
        self.ssh_session.close()
        self.client.close()
        plog.debug(f'{room_name} websocket is closed.')
        self.connect_status = False

    def __init_ssh(self, _format):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        auth_info = format_ssh_auth_data(_format)
        plog.debug(auth_info)
        msg = "connection succeeded\r\n"
        try:
            self.client.connect(timeout=5, **auth_info)
        except paramiko.ssh_exception.BadAuthenticationType as e:
            self.client = None
            msg = f"connection failed: {e}\r\n"
        except Exception as e:
            self.client = None
            plog.critical(e.__str__())
            msg = "connection failed\r\n"

        self.send(text_data=json.dumps({'message': msg}))

        if not hasattr(self.client, 'get_transport'):
            return

        self.ssh_session = self.client.get_transport().open_session()  # 成功连接后获取ssh通道
        self.ssh_session.settimeout(120)
        self.ssh_session.get_pty()
        self.ssh_session.invoke_shell()
        self.send(text_data=json.dumps({'message': '', 'code': 201}))

        for i in range(2):
            msg = self.ssh_session.recv(2048)
            self.send(text_data=json.dumps({'message': msg.decode("utf-8"), 'code': 200}))

    def get_work_dir(self):
        self.ssh_session.send('pwd \r')
        msg = self.ssh_session.recv(2048).decode("utf-8").split('\n')[1]
        msg = msg.split('\r')[1]
        self.current_work_dir = msg
        self.send(text_data=json.dumps(
            {'work_dir': msg, 'message': '', 'code': 200}))

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        if self.client:
            message = 'echo "invalid format request"\r'
            try:
                message = text_data_json['message']
            except:
                pass
            method = text_data_json.pop("method", "interactive")

            if method == "interactive":
                self.suspended_interactive = False
                self.ssh_session.send(message)
                if self.loop is None:
                    loop = Thread(target=self.ssh_recv, args=())
                    loop.start()
                    self.loop = loop
            elif hasattr(self, method):
                try:
                    self.suspended_interactive = True
                    getattr(self, method)()
                except Exception:
                    self.send(text_data=json.dumps(
                        {'work_dir': traceback.format_exc(), 'message': '', 'code': 500}))
        else:
            self.__init_ssh(text_data_json)
