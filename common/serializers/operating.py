import logging
import subprocess
import sys
import threading
import uuid

from rest_framework import serializers

from base.dataclass import BaseOperatingRes, BaseOperatingResEnum

logger = logging.getLogger(__name__)


class EmptySerializer(serializers.Serializer):
    pass


class QueryOperatingResSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=72)


class OperatingResultSerializer(serializers.Serializer):
    # BaseOperatingResEnum
    result = serializers.ChoiceField(
        choices=[(tag.name, tag.value) for tag in BaseOperatingResEnum], help_text="int"
    )
    result_text = serializers.CharField(max_length=72)


class OperatingResSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=72)
    result = serializers.ChoiceField(
        choices=[(tag.name, tag.value) for tag in BaseOperatingResEnum], help_text="int"
    )
    name = serializers.CharField(max_length=72)

    msg = serializers.CharField(max_length=256)
    result = OperatingResultSerializer()
    create_at = serializers.CharField(max_length=72)

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
        op = BaseOperatingRes(uuid.uuid4(), name="ExecuteCommandSync")
        cwd = validated_data.get("cwd")
        command = validated_data.get("command").replace("  ", " ").replace("  ", " ")

        ret = subprocess.Popen(
            command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        msg = "ok"

        if ret.returncode == 0:
            stdout = ret.stdout.read().decode("utf-8")
            if stdout != "":
                msg = stdout
            op.set_success()

        if ret.stderr:
            stderr = ret.stderr.read().decode("utf-8")
            if stderr != "":
                msg = stderr
                op.set_failure()
        else:
            msg = f"ExecuteCommandSyncSerializer#{sys._getframe().f_lineno}: unknown error."
            op.set_failure()

        op.msg = msg
        op.set_success()
        return op.json()


class ExecuteCommandAsyncSerializer(serializers.Serializer):
    """异步执行命令，返回event_id，通过event_id查询执行结果
    第一版方案: 使用多线程，通过event_id查询执行结果
    """

    cwd = serializers.CharField(max_length=255)
    command = serializers.CharField(max_length=1024)

    def run_thread(self, event_id, cwd, command):
        try:
            logging.debug(f"{event_id} {cwd} {command}")
            operator_res = BaseOperatingRes.get_instance(event_id)
            operator_res.set_processing()
            ret = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
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
        except Exception as e:
            msg = f"ExecuteCommandSyncSerializer#{sys._getframe().f_lineno}: {e}"
            logging.error(msg)
            operator_res.set_failure()

        operator_res.msg = msg
        logging.debug(f"op({event_id}) thread end.")

    def create(self, validated_data):
        operator_res = BaseOperatingRes(
            event_id=uuid.uuid4().hex, name="ExecuteCommandAsync"
        )

        threading.Thread(
            target=self.run_thread,
            args=(
                operator_res.event_id,
                validated_data.get("cwd"),
                validated_data.get("command"),
            ),
        ).start()

        return operator_res.json()
