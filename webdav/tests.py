from unittest import TestCase

from webdav.utils.webdav import append_server_nginx_config


# Create your tests here.

class NginxModifyTestCase(TestCase):

    def test_update_server_block(self):
        data = """server {
    listen 80 default_server;
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
    access_log  /var/log/nginx/uissh.log;
    error_log  /var/log/nginx/uissh.error.log;
}"""
        new_data = """location /webdav {
        proxy_pass http://127.0.0.1:1271;}"""
        expect_data = """server {
    listen 80 default_server;
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
    access_log /var/log/nginx/uissh.log;
    error_log /var/log/nginx/uissh.error.log;
    location /webdav {
        proxy_pass http://127.0.0.1:1271;
    }
}
"""
        test_data = append_server_nginx_config(data, new_data)
        self.assertEqual(test_data, expect_data)


