## Installation and requirements

1. Add `firebase_notifications` to requirements.txt/Pipfile/project.toml
2. Install requirements
3. Add application to django applications
4. Update `settings.py` with the keys described below
5. Migrate to create DB-Tables
6. Register URLs

## Required Settings

- `FCM_API_KEY`: API key for fcm service
- `FCM_USE_SESSION_USER`: If `True` require the connection of a device registration to a django user

## Python API

TODO

## Rest API

### GET `device-registration/<id>`

Fetch device registration, response is JSON:

```json
{
    "registration_id": "<id>",
    "registration_target": {
        "key": "value"
    }
}
```

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

May raise permission denied error if `registration_id` belongs to other user when `FCM_USE_SESSION_USER` is enabled.

### DELETE `device-registration/<id>`

Remove a device from all subscribed targets, body is empty.

May raise permission denied error if `registration_id` belongs to other user when `FCM_USE_SESSION_USER` is enabled.

