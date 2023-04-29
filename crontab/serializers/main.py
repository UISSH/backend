from base.serializer import ICBaseModelSerializer
from crontab.models.main import CrontabModel


class CrontabModelSerializer(ICBaseModelSerializer):
    class Meta:
        model = CrontabModel
        fields = "__all__"
