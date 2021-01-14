from firebase_notification.tasks import RegistrationIds
from firebase_notification.tasks import notify_multiple_devices, multiple_devices_data_message, process_fcm_response


def send_notification(registration_ids: RegistrationIds, message_body: str, message_title: str, **kwargs):
    return notify_multiple_devices.apply_async(
        args=(registration_ids, message_body, message_title),
        kwargs=kwargs,
        link=process_fcm_response.s(registration_ids)
    )


def send_data(registration_ids: RegistrationIds, data_message: dict, **kwargs):
    return multiple_devices_data_message.apply_async(
        args=(registration_ids, data_message),
        kwargs=kwargs,
        link=process_fcm_response.s(registration_ids)
    )
