from django.contrib import admin

# Register your models here.
from database.models import DataBaseModel


@admin.register(DataBaseModel)
class DataBaseAdmin(admin.ModelAdmin):
    pass
