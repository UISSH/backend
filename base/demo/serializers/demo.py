from base.serializer import ICBaseModelSerializer, ICBaseSerializer


class DemoModelSerializer(ICBaseModelSerializer):
    class Meta:
        model = object
        fields = '__all__'


class DemoSerializer(ICBaseSerializer):
    pass
