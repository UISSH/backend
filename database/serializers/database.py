from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from base.serializer import ICBaseModelSerializer
from database.models import DataBase


class DataBaseModelSerializer(ICBaseModelSerializer):
    own_username = serializers.SerializerMethodField(
        "_own_username", help_text="own username", label="own username"
    )
    create_status_text = serializers.SerializerMethodField("_create_status_text")
    database_type_text = serializers.SerializerMethodField("_database_type_text")

    class Meta:
        model = DataBase
        fields = "__all__"

    def validate_name(self, val: str):
        if "." in val:
            raise serializers.ValidationError(
                "Database name cannot contain '.' characters."
            )
        return val

    @extend_schema_field(
        serializers.CharField(read_only=True, help_text="own username")
    )
    def _own_username(self, instance: DataBase):
        return instance.user.username

    @extend_schema_field(serializers.CharField(read_only=True))
    def _database_type_text(self, instance: DataBase):
        return instance.get_database_type_display()

    @extend_schema_field(serializers.CharField(read_only=True))
    def _create_status_text(self, instance: DataBase):
        return instance.get_create_status_display()
