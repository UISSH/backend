import subprocess
import sys
import uuid
from rest_framework import serializers
from base.dataclass import BaseOperatingRes
from base.dataclass import BaseOperatingResEnum


class EmptySerializer(serializers.Serializer):
    pass


class QueryOperatingResSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=72)


class OperatingResSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=72)
    result = serializers.ChoiceField(
        choices=[(tag.name, tag.value) for tag in BaseOperatingResEnum], help_text="int"
    )
    msg = serializers.CharField(max_length=256)
    result_text = serializers.CharField(max_length=72)

    @staticmethod
    def get_operating_res(event_id=None) -> BaseOperatingRes:
        if event_id is None:
            event_id = uuid.uuid4().__str__()
        instance: BaseOperatingRes = BaseOperatingRes.get_instance(event_id)
        if instance is None:
            instance = BaseOperatingRes(event_id=event_id)
        return instance

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ExecuteCommandSyncSerializer(serializers.Serializer):
    cwd = serializers.CharField(max_length=255)
    command = serializers.CharField(max_length=1024)

    def create(self, validated_data):
        operator_res = BaseOperatingRes(name="ExecuteCommandSync")
        cwd = validated_data.get("cwd")
        command = validated_data.get("command").replace("  ", " ").replace("  ", " ")

        ret = subprocess.Popen(
            command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if ret.stdout:
            stdout = ret.stdout.read().decode("utf-8")
            if stdout != "":
                msg = stdout
                operator_res.set_success()

        if ret.stderr:
            stderr = ret.stderr.read().decode("utf-8")
            if stderr != "":
                msg = stderr
                operator_res.set_failure()
        else:
            msg = f"ExecuteCommandSyncSerializer#{sys._getframe().f_lineno}: unknown error."
            operator_res.set_failure()

        operator_res.msg = msg
        return operator_res.json()


class ExecuteCommandAsyncSerializer(serializers.Serializer):
    """异步执行命令，返回event_id，通过event_id查询执行结果
    第一版方案: 使用多线程，通过event_id查询执行结果
    """

    cwd = serializers.CharField(max_length=255)
    command = serializers.CharField(max_length=1024)

    def create(self, validated_data):
        operator_res = BaseOperatingRes()
        operator_res.set_not_support()
        return operator_res.json()
