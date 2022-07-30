import json
import traceback
from threading import Thread

import paramiko
from channels.generic.websocket import WebsocketConsumer
from rest_framework.authtoken.models import Token

from common.models import User


class SshWebConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user: User = None
        self.client = None
        self.ssh_session = None

    def ssh_recv(self):  # 从ssh通道获取输出data，并发送到前端
        print("ssh_recv")
        while True:
            msg = self.ssh_session.recv(2048)
            if not len(msg):
                print('退出监听发送循环')
                return
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

        self.client = paramiko.SSHClient()  # 创建连接对象
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        msg = "connection succeeded\r\n"
        try:
            self.client.connect(hostname="127.0.0.1", port=22, username="admin", key_filename="./id_rsa")
        except:
            msg = "connection failed\r\n"

        self.send(text_data=json.dumps({'message': msg}))

        self.ssh_session = self.client.get_transport().open_session()  # 成功连接后获取ssh通道
        self.ssh_session.get_pty()  # 获取一个终端
        self.ssh_session.invoke_shell()  # 激活终端
        self.send(text_data=json.dumps({'message': '', 'code': 201}))
        for i in range(2):  # 激活终端后会有信息流，一般都是lastlogin与bath目录，并获取其数据
            msg = self.ssh_session.recv(2048)
            self.send(text_data=json.dumps({'message': msg.decode("utf-8"), 'code': 200}))
        print("ok")

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = 'echo "请求无效格式"\r'
        try:
            message = text_data_json['message']
        except:
            pass
        self.ssh_session.send(message)
        # self.send(text_data=json.dumps({'message': message}))
        loop = Thread(target=self.ssh_recv, args=())
        loop.start()

    # import json  # from channels.generic.websocket import AsyncWebsocketConsumer  #  # class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
