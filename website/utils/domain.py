import logging
import os
import random
import string
import traceback

import requests


def resolve_domain(domain):
    # 使用 cloudflare doh 解析域名
    url = "https://cloudflare-dns.com/dns-query"
    params = {"name": domain, "type": "A"}
    headers = {"Content-Type": "application/dns-json"}
    data = requests.post(url, params=params, headers=headers)
    # get type is "1" record
    logging.debug(data.text)
    try:
        for i in data.json()["Answer"]:
            if i["type"] == 1:
                return i["data"]
    except:
        return


def find_local_public_ip():
    requests.get("http://checkip.amazonaws.com")
    return requests.get("http://checkip.amazonaws.com").text


def find_domain_in_nginx():
    """
    从 nginx 配置文件中获取域名
    """
    path = "/etc/nginx/sites-enabled/backend_ssl.conf"
    if not os.path.exists(path):
        path = "/etc/nginx/sites-enabled/backend.conf"

    if os.path.exists(path):
        data = open(path).read()
        try:
            domain = data.split("server_name")[1].split(";")[0].strip()
            return domain
        except Exception:
            logging.debug(traceback.format_exc())
            logging.debug("find domain in nginx error")

    return ""


def domain_is_resolved(domain, request):
    """
    构造一个目标为 domain 域名的IP地址， Host 为 UISSH 入口的请求
    """

    from rest_framework.authtoken.models import Token

    from base.dataclass import BaseOperatingRes
    from base.utils.cache import IBaseCache

    _cache = IBaseCache()
    op = BaseOperatingRes(uuid.uuid4().hex)
    op.set_processing()

    random_str = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(32)
    )
    _cache.set(domain, random_str)
    params = {"domain": domain}
    token = Token.objects.get(user=request.user)

    remote_ip = resolve_domain(domain)

    if remote_ip is None:
        op.msg = "The domain name has not been resolved to this host."
        op.set_failure()
        return op

    host = find_domain_in_nginx()
    url = f"https://{remote_ip}/api/Website/domain_records"

    headers = {"Authorization": f"token {token.key}", "host": f"{host}"}
    try:
        data = requests.get(
            url, params=params, headers=headers, timeout=5, verify=False
        )

        logging.info(data.text)

        if data.json()["msg"] == random_str:
            op.set_success()
        else:
            op.msg = "The domain name has not been resolved to this host."
            op.set_failure()
    except:
        logging.warn(f"Get {url}")
        logging.warn(f"Headers:\n {headers}")
        op.msg = f"{traceback.print_exc()}"
        op.set_failure()

    return op


if __name__ == "__main__":
    logging.debug(resolve_domain("example.com"))
    logging.debug(find_domain_in_nginx())
    logging.debug(requests.get("http://checkip.amazonaws.com").text)
