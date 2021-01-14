import json
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from django.conf import settings

from firebase_notification.tasks import update_device_info

from .models import FCMDevice
from .serializers import FCMDeviceSerializer


class DeviceRegistrationViewSet(ViewSet):
    lookup_field = 'registration_id'

    def create(self, request):
        """
        Custom endpoint to register the device (create or update)
        """
        registration_id = request.data.get('registration_id')
        if registration_id is None:
            raise ValidationError
        registration_target = request.data.get('registration_target')
        if registration_target is None:
            registration_target = {}
        else:
            registration_target = json.loads(registration_target)

        try:
            fcm_device = FCMDevice.objects.get(registration_id=registration_id)
        except FCMDevice.DoesNotExist:
            fcm_device = FCMDevice.objects.create(
                registration_id=registration_id,
                registration_target=registration_target,
                is_active=True
            )

        # same device, different channels
        if fcm_device.registration_target != registration_target:
            fcm_device.registration_target = registration_target
            fcm_device.save()

        # same device, different user
        if settings.FCM_USE_SESSION_USER:
            if fcm_device.user != request.user:
                fcm_device.user = request.user
                fcm_device.save()

        # update device infos (enable device on success if required)
        update_device_info.delay(fcm_device.registration_id)

        serializer = FCMDeviceSerializer(fcm_device)

        return Response(serializer.data)

    def destroy(self, request, registration_id=None):
        """
        Custom endpoint to unregister (disable) the device
        """
        if registration_id is None:
            raise ValidationError

        try:
            fcm_device = FCMDevice.objects.get(registration_id=registration_id)
        except FCMDevice.DoesNotExist:
            raise NotFound

        # if user connection is enabled check for permission
        if settings.FCM_USE_SESSION_USER:
            if fcm_device.user != request.user:
                raise PermissionDenied

        # disable device
        fcm_device.is_active = False
        fcm_device.save()

        serializer = FCMDeviceSerializer(fcm_device)

        return Response(serializer.data)
