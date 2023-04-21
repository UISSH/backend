from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request

from base.viewset import BaseModelViewSet, BaseReadOnlyModelViewSet
from common.models.User import User
from common.serializers.user import (
    CreateUserSerializer,
    AdminUserSerializer,
    UserLoginSerializer,
    UserSerializer,
    UpdatePasswordSerializer,
    UserLoginResSerializer,
)


class AdminUserView(BaseModelViewSet):
    permission_classes = (permissions.IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username"]
    filterset_fields = ["username", "email"]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object().user
        user.is_active = False
        user.save()
        return self.base_response("成功限制用户登录")


class UserView(BaseReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username"]
    filterset_fields = ["username", "email"]

    def get_queryset(self):
        return self.queryset.filter(pk=self.request.user.id)

    @transaction.atomic
    @action(methods=["POST"], detail=False, permission_classes=[permissions.AllowAny])
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.base_response(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={"200": UserLoginResSerializer})
    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[permissions.AllowAny],
        serializer_class=UserLoginSerializer,
    )
    def login(self, request, *args, **kwargs):
        """
        登录接口，email 与 username 至少传一项
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user: User = None
            token, user = serializer.save()
            return self.base_response(
                {"token": f"{token}", "username": user.username, "email": user.email},
                status=status.HTTP_200_OK,
            )
        else:
            return self.base_response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=["POST"], detail=False, permission_classes=[permissions.AllowAny])
    def forget_password(self, request, *args, **kwargs):
        return self.base_response(
            {"msg": "该接口尚未实现"}, status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # @vary_on_headers('anonymous', 'authorization')
    # @method_decorator(cache_page(30))
    @action(
        methods=["get"], detail=False, permission_classes=[permissions.IsAuthenticated]
    )
    def status(self, request: Request, *args, **kwargs):
        user: User = request.user
        user = User.objects.select_related(
            "quota", "quota__billing_plan", "quota_storage", "quota_network"
        ).get(pk=user.id)
        serializer = UserSerializer(user)
        return self.base_response(serializer.data)

    @extend_schema(responses=UserSerializer)
    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UpdatePasswordSerializer,
    )
    def update_password(self, request: Request, *args, **kwargs):
        serializer = UpdatePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return self.base_response(data)
