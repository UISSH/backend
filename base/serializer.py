from pprint import pprint

from rest_framework import serializers

from common.models.User import User


class ICBaseSerializer(serializers.Serializer):
    def get_user(self) -> User:
        """
        获取用户，初始化序列的时候，请添加 context={'request': request}，
        :return:
        """
        request = self.context.get("request", None)
        if request:
            return request.user

        raise RuntimeError(
            f"无法获取用户，请在初始化{self.__class__.__name__}的时候添加参数 context={'request': request}"
        )


class ICBaseModelSerializer(serializers.ModelSerializer):
    @staticmethod
    def _log(data: dict):
        pprint(data)

    def get_user(self) -> User:
        """
        获取用户，初始化序列的时候，请添加 context={'request': request}，
        :return:
        """
        request = self.context.get("request", None)
        if request:
            return request.user

        raise RuntimeError(
            f"无法获取用户，请在初始化{self.__class__.__name__}的时候添加参数 context={'request': request}"
        )
