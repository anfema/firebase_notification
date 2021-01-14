from django.contrib import admin

from .models import FCMDevice

# Register your models here.


@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
	search_fields = ('user', 'registration_target')
	list_filter = ('user', 'platform', 'is_active', 'app_version')
	list_display = ('user', 'platform', 'is_active', 'app_version', 'created_at', 'updated_at')
	readonly_fields = ('created_at', 'updated_at')
