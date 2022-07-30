import os
import pathlib
import time

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from base.viewset import BaseModelViewSet
from common.config import DB_SETTINGS
from common.models import User
from common.serializers.operating import OperatingResSerializer
from database.models import DataBase
from database.models.database_utils import export_backup_db, import_backup_db
from database.serializers.database import DataBaseModelSerializer


class DataBaseView(BaseModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = DataBase.objects.select_related("user").all()
    serializer_class = DataBaseModelSerializer

    # lookup_field = "username"

    def get_queryset(self):
        user: User = self.request.user
        if user.is_superuser:
            return self.queryset.order_by("-create_at").all()
        else:
            return self.queryset.order_by("-create_at").filter(user=user)

    @action(methods=["post"], detail=True, serializer_class=OperatingResSerializer)
    def create_instance(self, request, *args, **kwargs):
        obj: DataBase = self.get_object()
        op_res = obj.get_operating_res()

        if obj.create_status == obj.CreateStatus.FAILED:
            op_res.msg = "Database already exists."
            op_res.set_failure()
            return Response(op_res.json())

        obj.create_database_instance(op_res.event_id)

        return Response(op_res.json())

    @action(methods=['get'], detail=False, serializer_class=OperatingResSerializer)
    def query_database_run_status(self, request, *args, **kwargs):

        stats = os.system("systemctl is-active -q mariadb")
        if stats == 0:
            msg = "active"
        else:
            msg = "inactive"
        op_res = DataBase.get_operating_res()
        op_res.set_processing()
        op_res.msg = msg
        op_res.set_success()
        return Response(op_res.json())

    @action(methods=["get"], detail=False, serializer_class=OperatingResSerializer)
    def start_database_instance(self, request, *args, **kwargs):
        op_res = DataBase.get_operating_res()
        op_res.set_processing()
        stats = os.system("systemctl start mariadb")
        if stats == 0:
            op_res.set_success()
        else:
            op_res.msg = f"run 'systemctl start mariadb' exit code: {stats}"
            op_res.set_failure()
        return Response(op_res.json())

    @action(methods=["get"], detail=False, serializer_class=OperatingResSerializer)
    def stop_database_instance(self, request, *args, **kwargs):
        op_res = DataBase.get_operating_res()
        op_res.set_processing()
        stats = os.system("systemctl stop mariadb")
        if stats == 0:
            op_res.set_success()
        else:
            op_res.msg = f"run 'systemctl stop mariadb' exit code: {stats}"
            op_res.set_failure()

        return Response(op_res.json())

    @action(methods=["get"], detail=False, serializer_class=OperatingResSerializer)
    def restart_database_instance(self, request, *args, **kwargs):
        op_res = DataBase.get_operating_res()
        op_res.set_processing()
        stats = os.system("systemctl restart mariadb")
        if stats == 0:
            op_res.set_success()
        else:
            op_res.msg = f"run 'systemctl restart mariadb' exit code: {stats}"
            op_res.set_failure()
        return Response(op_res.json())

    @extend_schema(parameters=[OpenApiParameter(name='str', type=str)])
    @action(methods=['post'], detail=True, serializer_class=OperatingResSerializer)
    def import_backup(self, request: Request, *args, **kwargs):
        op_res = DataBase.get_operating_res()
        path = request.query_params.get('path', None)
        if path is None:
            op_res.msg = f'`path` parameter is required.'
            op_res.set_failure()
            return Response(op_res.json())
        if not pathlib.Path(path).exists():
            op_res.msg = f'{path} does not exist. '
            op_res.set_failure()
            return Response(op_res.json())

        root_username = DB_SETTINGS.database_value()['database']['root_username']
        root_password = DB_SETTINGS.database_value()['database']['root_password']
        import_backup_db(op_res.event_id, backup_db_path=path, root_username=root_username, root_password=root_password)
        return Response(op_res.json())

    @action(methods=['post'], detail=True, serializer_class=OperatingResSerializer)
    def export_backup(self, request: Request, *args, **kwargs):

        op_res = DataBase.get_operating_res()
        root_username = DB_SETTINGS.database_value()['database']['root_username']
        root_password = DB_SETTINGS.database_value()['database']['root_password']
        obj: DataBase = self.get_object()
        backup_db_path = f'{obj.get_backup_dir()}/{int(time.time())}.sql'
        export_backup_db(op_res.event_id, obj.name, backup_db_path=backup_db_path,
                         root_username=root_username, root_password=root_password)
        op_res.msg = backup_db_path

        return Response(op_res.json())

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
