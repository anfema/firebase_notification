from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField


class FCMDevice(models.Model):
    FCM_PLATFORMS = (
        ("ANDROID", "Android"),
        ("IOS", "iOS"),
        ("CHROME", "Web"),
    )

    registration_id = models.CharField(unique=True, max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    registration_target = JSONField(blank=True, default=dict)
    is_active = models.BooleanField(default=True, help_text=_("Inactive devices will not be sent notifications"))
    platform = models.CharField(choices=FCM_PLATFORMS, max_length=7, null=True, blank=True)
    connect_date = models.DateField(null=True, blank=True)
    app_version = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Registration <{self.registration_target}> for device on {self.platform}"
