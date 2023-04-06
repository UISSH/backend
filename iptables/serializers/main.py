from base.serializer import ICBaseModelSerializer, ICBaseSerializer
from rest_framework import serializers

class IPTablesRuleListSerializer(ICBaseSerializer):
    ID  = serializers.IntegerField(help_text=1)
    To = serializers.CharField(help_text="22/tcp")
    Action = serializers.CharField(help_text="ALLOW")
    From = serializers.CharField(help_text="Anywhere")
    
