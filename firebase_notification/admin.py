from django.contrib import admin
from django.conf import settings

from .models import FCMDevice
# Register your models here.


if settings.FCM_USE_SESSION_USER:
	@admin.register(FCMDevice)
	class FCMDeviceAdmin(admin.ModelAdmin):
		search_fields = ('user', 'registration_target')
		list_filter = ('user', 'platform', 'is_active', 'app_version')
		list_display = ('user', 'platform', 'is_active', 'app_version', 'created_at', 'updated_at', 'registration_id')
		list_display_links = ('registration_id',)
		readonly_fields = ('created_at', 'updated_at')
else:
	@admin.register(FCMDevice)
	class FCMDeviceAdmin(admin.ModelAdmin):
		search_fields = ('registration_target', )
		list_filter = ('platform', 'is_active', 'app_version')
		list_display = ('platform', 'is_active', 'app_version', 'created_at', 'updated_at', 'registration_id')
		list_display_links = ('registration_id',)
		readonly_fields = ('created_at', 'updated_at')
