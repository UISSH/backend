from base.serializer import ICBaseModelSerializer
from common.models import KVStorage


class KVStorageSerializer(ICBaseModelSerializer):
    class Meta:
        model = KVStorage
        fields = "__all__"
