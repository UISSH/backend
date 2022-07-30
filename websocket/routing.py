from django.urls import re_path

from .apis import ssh_web, consumers, server_status

websocket_urlpatterns = [
    re_path(r'ws/websocket/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/terminal/$', ssh_web.SshWebConsumer.as_asgi()),
    re_path(r'ws/server_status/$', server_status.ServerStatusConsumer.as_asgi()),
]
