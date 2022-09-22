from django.contrib import admin

from ftpserver.models import FtpServerModel


# Register your models here.
@admin.register(FtpServerModel)
class FtpServerModelAdmin(admin.ModelAdmin):
    pass
