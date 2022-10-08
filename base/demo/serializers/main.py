from base.serializer import ICBaseModelSerializer, ICBaseSerializer


class MainModelSerializer(ICBaseModelSerializer):
    class Meta:
        model = object
        fields = '__all__'


class MainSerializer(ICBaseSerializer):
    pass
