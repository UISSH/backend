from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    # 主要增加邮箱地址唯一约束
    email = models.EmailField(_('email address'), blank=True, unique=True)
    avatar = models.URLField(default=None, blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(User, self).save(*args, **kwargs)
        if is_new:
            token, _ = Token.objects.get_or_create(user=self)
            Token.objects.filter(pk=token.key).update(key=token.generate_key())
