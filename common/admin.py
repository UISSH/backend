# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from common.models import SystemConfigModel, User

# Register your models here.
admin.site.register(User, UserAdmin)


@admin.register(SystemConfigModel)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "enable", "module_name"]
    list_editable = ["enable"]
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }
