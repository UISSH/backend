import random
import socket
import string
import traceback

import requests
from rest_framework.authtoken.models import Token

from base.dataclass import BaseOperatingRes
from base.utils.cache import IBaseCache


def domain_is_resolved(domain, request):
    _cache = IBaseCache()
    op = BaseOperatingRes()
    op.set_processing()
    random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    _cache.set(domain, random_str)
    params = {"domain": domain}
    token = Token.objects.get(user=request.user)
    try:
        # url = "http://" + f"{socket.gethostbyname(domain)}/api/Website/domain_records"
        url = "http://" + f"{domain}/api/Website/domain_records"
        headers = {"Authorization": f"token {token.key}"}
        data = requests.get(url, params=params, headers=headers, timeout=5)

        if data.json()["msg"] == random_str:
            op.set_success()
        else:
            op.msg = "The domain name has not been resolved to this host."
            op.set_failure()
    except:
        op.msg = f"{traceback.print_exc()}"
        op.set_failure()

    return op
