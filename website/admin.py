from django.contrib import admin

# Register your models here.
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from website.models import WebsiteModel


@admin.register(WebsiteModel)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ["name", "domain", "ssl_enable"]
    list_editable = ["ssl_enable"]
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }
