from rest_framework import routers

from .views import DeviceRegistrationViewSet

router = routers.SimpleRouter()
router.register(r'device-registration', DeviceRegistrationViewSet, basename='device')

urlpatterns = router.urls
