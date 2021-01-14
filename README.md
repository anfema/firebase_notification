## Installation and requirements

Please refer to [celery documentation](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html) on how to integrate celery before you start with this.

1. Add `firebase_notifications` to `requirements.txt`/`Pipfile`/`project.toml`
2. Install requirements
3. Add application to django applications
```python
INSTALLED_APPS = [
    ...
    'firebase_notification'
    ...
```
4. Update `settings.py` with the keys described below
```python
# Firebase settings
FCM_USE_SESSION_USER = False
FCM_API_KEY = 'foobar'
```
5. Migrate to create DB-Tables: `python manage.py migrate`
6. Register URLs in `urls.py`
```python
urlpatterns = [
    ...
    path('', include('firebase_notification.urls')),
    ...
]
```
7. Make sure to run a celery worker in parallel to your python application server:
```bash
celery worker --app=yourproject.celery
```

## Required Settings

- `FCM_API_KEY`: API key for fcm service
- `FCM_USE_SESSION_USER`: If `True` require the connection of a device registration to a django user

## Python API

All python API is in the `messaging` module:

```python
from firebase_notification.messaging import send_notification, send_data
```

### Sending a push notification

```python
def send_notification(registration_ids: RegistrationIds, message_body: str, message_title: str, **kwargs)
```

To send a notification to one or more devices call this function with a list of registration ids. To fetch the needed registration ids you can use the `FCMDevice` model to filter out devices you want to process

### Sending a data-only push notification (aka. silent push)

```python
def send_data(registration_ids: RegistrationIds, data_message: dict, **kwargs)
```

You can send a silent push notification with only data attached to trigger a content download on the
device by using this function. As with `send_notification` you can use the `FCMDevice` model to get to the registration ids

### `FCMDevice` - Model

```python
from firebase_notification.models import FCMDevice
```

You have multiple options to select a device to send a notification to:

1. Just send to all devices of a `platform`
2. If user to device registration is enabled (`FCM_USE_SESSION_USER`) you can use the `user` attribute
3. Furthermore you can use the JSON field `registration_target` to save any additional meta-data to the model for the application logic to filter for (like user preferences on what push notifications the user wants to subscribe to, etc.)

Please be sure to only send notifications to devices that have the `is_active` flag set. The flag is updated when calling the FCM API and getting an error to avoid spamming unregistered or blocked devices to the API.

## Rest API

### POST `device-registration`

Create or update a device subscription, request is JSON:

```json
{
    "registration_id": "<fcm_token>",
    "registration_target": {
        "key": "value"
    }
}
```

May raise validation error if `registration_id` is missing

Will overwrite the connected user to the calling session user if `FCM_USE_SESSION_USER` is enabled.

### DELETE `device-registration/<fcm_token>`

Remove a device from all subscribed targets, body is empty.

May raise permission denied error if `registration_id` belongs to other user when `FCM_USE_SESSION_USER` is enabled.

