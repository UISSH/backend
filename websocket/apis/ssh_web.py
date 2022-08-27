import base64
import json
import traceback
from io import StringIO

from threading import Thread

import paramiko
from channels.generic.websocket import WebsocketConsumer
from rest_framework.authtoken.models import Token

from base.utils.logger import plog
from common.models import User


class SshWebConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user: User = None
        self.client = None
        self.ssh_session = None
        self.connect_status = False

    def ssh_recv(self):
        while True:
            if self.connect_status is False:
                break
            msg = self.ssh_session.recv(2048)
            if not len(msg):
                break
            self.send(text_data=json.dumps({'message': msg.decode("utf-8"), 'code': 200}))

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
        self.connect_status = True

    def disconnect(self, close_code):
        self.connect_status = False

    def __init_ssh(self, _format):
        self.client = paramiko.SSHClient()  # 创建连接对象
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        private_key = _format.pop("private_key", None)
        private_key_password = _format.pop("private_key_password", None)

        if private_key:
            private_key = StringIO(private_key)
            if private_key_password:
                pkey = paramiko.RSAKey.from_private_key(private_key, password=private_key_password)
            else:
                pkey = paramiko.RSAKey.from_private_key(private_key)

            private_key.close()
            del _format["password"]
            auth_info = _format
            auth_info["pkey"] = pkey

        elif not _format.get('password', None):
            # If there is no password and certificate,
            # try to use the certificate file in the project root directory for testing.
            plog.warning("Use project root certificate.")
            pkey = paramiko.RSAKey.from_private_key(open('./test.pem'))
            auth_info = _format
            auth_info["pkey"] = pkey

        else:
            auth_info = _format

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
        self.ssh_session.get_pty()  # 获取一个终端
        self.ssh_session.invoke_shell()  # 激活终端
        self.send(text_data=json.dumps({'message': '', 'code': 201}))
        for i in range(2):  # 激活终端后会有信息流，一般都是lastlogin与bath目录，并获取其数据
            msg = self.ssh_session.recv(2048)
            self.send(text_data=json.dumps({'message': msg.decode("utf-8"), 'code': 200}))

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        if self.client:
            message = 'echo "请求无效格式"\r'
            try:
                message = text_data_json['message']
            except:
                pass
            self.ssh_session.send(message)
            # self.send(text_data=json.dumps({'message': message}))
            loop = Thread(target=self.ssh_recv, args=())
            loop.start()
        else:
            self.__init_ssh(text_data_json)
