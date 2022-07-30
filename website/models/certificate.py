from django.db import models

from base.base_model import BaseModel
from common.models.User import User


class AcmeDNS(BaseModel):
    pass


class AcmeAccount(BaseModel):
    """
    用于注册 certbot 帐号的信息记录，每添加一个新的账户需要调用脚本注册并更新注册状态。
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    name = models.CharField(default="默认", max_length=64, unique=True, verbose_name="名称")
    server = models.URLField(default="https://acme-v02.api.letsencrypt.org/directory", verbose_name="签发服务")
    eab_kid = models.CharField(max_length=512, null=True, blank=True, verbose_name="kid")
    eab_hmac_key = models.CharField(max_length=512, null=True, blank=True, verbose_name="hmac_key")
    account_email = models.CharField(max_length=128, verbose_name="帐号邮箱")
    status = models.BooleanField(default=False, verbose_name="有效")

    def _send_create_event(self, *args, **kwargs):
        """
        发送新建事件，去调用脚本。
        :param args:
        :param kwargs:
        :return:
        """
