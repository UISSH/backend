from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from rest_framework import serializers


class IPTablesRuleSerializer(ICBaseSerializer):
    id = serializers.IntegerField(help_text=1)
    to = serializers.CharField(help_text="22/tcp")
    action = serializers.CharField(help_text="ALLOW")
    from_src = serializers.CharField(help_text="Anywhere")
