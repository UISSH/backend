from rest_framework import serializers

from base.dataclass import BaseOperatingResEnum


class EmptySerializer(serializers.Serializer):
    pass


class QueryOperatingResSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=72)


class OperatingResSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=72)
    result = serializers.ChoiceField(choices=[(tag.name, tag.value) for tag in BaseOperatingResEnum], help_text="int")
    msg = serializers.CharField(max_length=256)
    result_text = serializers.CharField(max_length=72)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
