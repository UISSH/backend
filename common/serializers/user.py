from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueTogetherValidator

from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from common.models.User import User


class BaseUserSerializer(ICBaseModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {"password": {"write_only": True}}

    # noinspection PyMethodMayBeStatic
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value

    def create(self, validated_data):
        user = User(email=validated_data["email"], username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class AdminUserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ["id"]
        extra_kwargs = {"password": {"write_only": True}}


class UserSerializer(ICBaseModelSerializer):
    isAdmin = serializers.SerializerMethodField("_is_admin")
    isActive = serializers.SerializerMethodField("_is_active")

    class Meta:
        model = User
        fields = ["username", "email", "isAdmin", "isActive"]

    def _is_admin(self, obj: User) -> bool:
        return obj.is_anonymous

    def _is_active(self, obj: User) -> bool:
        return obj.is_active


class CreateUserSerializer(ICBaseModelSerializer):
    def create(self, validated_data):
        password = validated_data.get("password", None)
        instance: User = super(CreateUserSerializer, self).create(validated_data)
        instance.set_password(password)
        instance.save()
        return instance

    def validate_email(self, val):
        if User.objects.filter(email=val).exists():
            raise serializers.ValidationError(f"{val} 邮箱已被使用")
        else:
            return val

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {"password": {"write_only": True}}

        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(), fields=["username", "email"]
            )
        ]


class UpdatePasswordSerializer(ICBaseSerializer):
    o_password = serializers.CharField(label="旧密码")
    n_password = serializers.CharField(label="新密码")

    def create(self, validated_data):
        n_password = validated_data.get("n_password")
        user = self.get_user()
        user.set_password(n_password)
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        Token.objects.filter(pk=token.key).update(key=token.generate_key())

        return UserSerializer(user).data

    def validate_o_password(self, val):
        user = self.get_user()
        user = authenticate(username=user.username, password=val)
        if user is None:
            raise serializers.ValidationError("密码错误")
        return val


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    email = serializers.EmailField(label="邮箱")
    password = serializers.CharField(min_length=6, label="密码")

    class Meta:
        # ToDo items belong to a parent list, and have an ordering defined
        # by the 'position' field. No two items in a given list may share
        # the same position.
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(), fields=["username", "email"]
            )
        ]

    def create(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")

        print(attrs)
        return attrs

    # def validate(self, attrs):
    #     username = attrs.get('username')
    #     email = attrs.get('email')
    #     password = attrs.get('password')
    #
    #     if User.objects.filter(username=username).exists():
    #         raise serializers.ValidationError({'username': '用户名已被注册'})
    #     elif User.objects.filter(email=email).exists():
    #         raise serializers.ValidationError({'email': '邮箱已被注册'})
    #     elif len(password) < 6:
    #         raise serializers.ValidationError({'password': '密码过短'})
    #     return attrs


class UserLoginResSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=1, label="token")
    email = serializers.EmailField(required=False, label="邮箱", help_text="邮箱与用户名必填一项")
    username = serializers.CharField(
        min_length=1, required=False, label="用户名", help_text="邮箱与用户名必填一项"
    )


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, label="邮箱", help_text="邮箱与用户名必填一项")
    username = serializers.CharField(
        min_length=1, required=False, label="用户名", help_text="邮箱与用户名必填一项"
    )
    password = serializers.CharField(min_length=1, label="密码")

    def create(self, validated_data):
        """
        save() 调用的方法，返回用户的Token
        """
        m_user = User.objects.get(
            Q(username=validated_data.get("username"))
            | Q(email=validated_data.get("email"))
        )
        m_user.last_login = timezone.now()
        m_user.save()
        token, created = Token.objects.get_or_create(user=m_user)

        single_point_login = False
        # TODO 存在且用户打开单点登陆开关 则更新 token 使上一个 key 失效
        if not created and single_point_login:
            Token.objects.filter(pk=token.key).update(key=token.generate_key())
            token = Token.objects.get(user=m_user)
        return token.key, m_user

    def validate(self, data):
        """
        登录验证，成功返回数据
        """
        data_dict = dict(data)
        username = data_dict.get("username")
        email = data_dict.get("email")
        password = data_dict.get("password")
        if not username and not email:
            msg = "用户名和邮箱必填其中一个"
            raise serializers.ValidationError({"username": msg, "email": msg})

        try:
            m_user = User.objects.get(Q(username=username) | Q(email=email))
        except User.DoesNotExist as e:
            if username:
                raise serializers.ValidationError({"username": "用户名不存在"})
            elif email:
                raise serializers.ValidationError({"email": "邮箱不存在"})
            else:
                raise serializers.ValidationError(
                    {"username": "用户不存在", "email": "用户不存在"}
                )

        user = authenticate(username=m_user.username, password=password)

        if not m_user.is_active:
            msg = "该账号被限制登录，请联系管理员"
            raise serializers.ValidationError({"username": msg, "email": msg})

        elif user is None:
            raise serializers.ValidationError({"password": "密码错误"})

        elif user is not None:
            # 授权通过，无需处理
            return data
