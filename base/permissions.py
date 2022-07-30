from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from common.models.User import User


class IsAdminOrAuthenticatedReadOnly(permissions.BasePermission):
    """
    检查权限
    """

    def has_permission(self, request, view):
        # 检查是否认证
        if not bool(request.user and request.user.is_authenticated):
            return False
        user: User = request.user

        if request.method in SAFE_METHODS:
            # 认证后，在('GET', 'HEAD', 'OPTIONS')
            return True
        elif user.is_superuser:
            # 其他请求，是管理员就通过
            return True
        else:
            return False
