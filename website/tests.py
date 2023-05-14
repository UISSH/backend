import os
import pathlib
import time

from django.test import TestCase

from website.applications.app_factory import AppFactory
from website.applications.core.dataclass import WebSiteConfig, WebServerTypeEnum

# Create your tests here.
from website.models.utils import (
    update_nginx_server_name,
    disable_section,
    get_section,
    insert_section,
    enable_section,
)

nginx_data = """server {

       ########BASIC########
       
       listen 80;
       listen [::]:80;
       server_name www.domain.com;
       
       ########BASIC########


       ########SSL########
       
       listen 443 ssl http2;
       listen [::]:443 ssl http2;
       ssl_certificate         /etc/letsencrypt/live/www.domain.com/fullchain.pem;
       ssl_certificate_key     /etc/letsencrypt/live/www.domain.com/privkey.pem;
       ssl_trusted_certificate /etc/letsencrypt/live/www.domain.com/chain.pem;

       ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
       ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
       ssl_prefer_server_ciphers on;
       ssl_session_cache shared:SSL:10m;
       ssl_session_timeout 10m;
       error_page 497  https://$host$request_uri;
       
       ########SSL########


       ########USER########
       
       # Please add your desired configuration here.
       
       ########USER########
       
       ########APP########

       root /var/www/www.domain.com;
       index index.html;

       location / {
               try_files $uri $uri/ =404;
       }
       
       ########APP########

}"""


class TestUpdateNginxServerName(TestCase):
    def test_domain(self):
        domain = "test.domain.com"
        sub_domain = (
            "test1.domain.com test2.domain.com test3.domain.com test4.domain.com"
        )
        data = update_nginx_server_name(nginx_data, domain, sub_domain)
        self.assertIn(f"server_name {domain} {sub_domain};", data)

    def test_null_sub_domain(self):
        domain = "test.domain.com"
        sub_domain = None
        data = update_nginx_server_name(nginx_data, domain, sub_domain)
        self.assertIn(f"server_name {domain};", data)


class TestNginxConfigTools(TestCase):
    def test_get_section(self):
        _data = """       listen 443 ssl http2;
       listen [::]:443 ssl http2;
       ssl_certificate         /etc/letsencrypt/live/www.domain.com/fullchain.pem;
       ssl_certificate_key     /etc/letsencrypt/live/www.domain.com/privkey.pem;
       ssl_trusted_certificate /etc/letsencrypt/live/www.domain.com/chain.pem;

       ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
       ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
       ssl_prefer_server_ciphers on;
       ssl_session_cache shared:SSL:10m;
       ssl_session_timeout 10m;
       error_page 497  https://$host$request_uri;"""
        data = get_section(nginx_data, "ssl")
        self.assertIn(_data, data)

    def test_insert_section(self):
        _data = """
    if ($http_user_agent ~* (SemrushBot|python|MJ12bot|AhrefsBot|AhrefsBot|hubspot|opensiteexplorer|leiki|webmeup)) {
        return 444;
    }"""
        data2 = "########USER########" + _data + "########USER########"

        self.assertIn(data2, insert_section(nginx_data, _data, "user"))

    def test_disable_section(self):
        _data = """       ########SSL########
       
       #**#listen 443 ssl http2;
       #**#listen [::]:443 ssl http2;
       #**#ssl_certificate         /etc/letsencrypt/live/www.domain.com/fullchain.pem;
       #**#ssl_certificate_key     /etc/letsencrypt/live/www.domain.com/privkey.pem;
       #**#ssl_trusted_certificate /etc/letsencrypt/live/www.domain.com/chain.pem;

       #**#ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
       #**#ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
       #**#ssl_prefer_server_ciphers on;
       #**#ssl_session_cache shared:SSL:10m;
       #**#ssl_session_timeout 10m;
       #**#error_page 497  https://$host$request_uri;
       
       ########SSL########"""
        self.assertIn(_data, disable_section(nginx_data, "ssl"))

    def test_enable_section(self):
        _data = disable_section(nginx_data, "ssl")

        self.assertEqual(nginx_data, enable_section(_data, "ssl"))


class TestApplication(TestCase):
    def test_load_app(self):
        app_factory = AppFactory
        app_factory.load()

        target_dir = f"/tmp/{int(time.time())}.com/"
        text = (
            "Python is a high-level, interpreted, general-purpose programming language. "
            "Its design philosophy emphasizes code readability with the use of significant indentation."
        )
        path = pathlib.Path(target_dir)
        if not path.exists():
            pathlib.Path(target_dir).mkdir()

        config = WebSiteConfig(
            domain="hello11.com",
            root_dir=target_dir,
            web_server_type=WebServerTypeEnum.Nginx,
        )

        app = app_factory.get_application_module(
            "NginxApplication",
            config,
            {"name": "hello", "text": text, "email": "hello@hello.com"},
        )
        for item in [
            "name",
            "author",
            "website_url",
            "docs_url",
            "download_url",
            "name_version",
            "code_version",
            "agreement_name",
            "description",
            "agreement_url",
        ]:
            self.assertIn(item, app.version().__dict__)
        res = app.create()
        self.assertTrue(res.is_success())
        os.system(f"rm -rf {target_dir}")
