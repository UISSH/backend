from base.serializer import ICBaseModelSerializer
from common.models import KVStorageModel


class KVStorageSerializer(ICBaseModelSerializer):
    class Meta:
        model = KVStorageModel
        fields = "__all__"
