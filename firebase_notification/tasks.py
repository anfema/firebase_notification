# Create your tasks here
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from typing import List, Set, Union

from django.conf import settings

from celery import shared_task
from pyfcm import FCMNotification
from pyfcm.errors import FCMServerError
from requests import HTTPError, Timeout

from firebase_notification.models import FCMDevice

RegistrationIds = Union[List[str], Set[str]]

"""
This file contains various tasks to work with the FCM API.

NOTE:
Use the shortcut functions from the `.messaging` module to send
notifications & data messages!
"""

FCM_RETRY_EXCEPTIONS = (FCMServerError, HTTPError, Timeout)


@shared_task(autoretry_for=FCM_RETRY_EXCEPTIONS, retry_backoff=True)
def notify_single_device(registration_id: str, message_body: str, message_title: str, **kwargs):
	push_service = FCMNotification(api_key=settings.FCM_API_KEY)
	return push_service.notify_single_device(
		registration_id=registration_id,
		message_body=message_body,
		message_title=message_title,
		**kwargs
	)


@shared_task(autoretry_for=FCM_RETRY_EXCEPTIONS, retry_backoff=True)
def notify_multiple_devices(registration_ids: RegistrationIds, message_body: str, message_title: str, **kwargs):
	push_service = FCMNotification(api_key=settings.FCM_API_KEY)
	return push_service.notify_multiple_devices(
		registration_ids=registration_ids,
		message_body=message_body,
		message_title=message_title,
		**kwargs
	)


@shared_task(autoretry_for=FCM_RETRY_EXCEPTIONS, retry_backoff=True)
def single_device_data_message(registration_id: str, data_message: dict, **kwargs):
	push_service = FCMNotification(api_key=settings.FCM_API_KEY)
	return push_service.single_device_data_message(
		registration_id=registration_id,
		data_message=data_message,
		**kwargs
	)


@shared_task(autoretry_for=FCM_RETRY_EXCEPTIONS, retry_backoff=True)
def multiple_devices_data_message(registration_ids: RegistrationIds, data_message: dict, **kwargs):
	push_service = FCMNotification(api_key=settings.FCM_API_KEY)
	return push_service.multiple_devices_data_message(
		registration_ids=registration_ids,
		data_message=data_message,
		**kwargs
	)


@shared_task(autoretry_for=FCM_RETRY_EXCEPTIONS, retry_backoff=True)
def update_device_info(registration_id: str):
	"""
	Task used to fetch device status information from the google Instance ID service
	"""
	if not settings.FCM_API_KEY:
		return

	push_service = FCMNotification(api_key=settings.FCM_API_KEY)
	response = push_service.registration_info_request(registration_id)
	if response.status_code == 200:
		# expect the device to be known
		response_json = response.json()
		device = FCMDevice.objects.get(registration_id=registration_id)
		device_updated = False

		if not device.is_active:
			device.is_active = True
			device_updated = True

		if device.platform != response_json.get('platform'):
			device.platform = response_json.get('platform')
			device_updated = True

		# connectDate is optional
		if response_json.get('connectDate'):
			connect_date = datetime.strptime(response_json.get('connectDate'), '%Y-%m-%d').date()
			if device.connect_date != connect_date:
				device.connect_date = connect_date
				device_updated = True

		if device.app_version != response_json.get('applicationVersion'):
			device.app_version = response_json.get('applicationVersion')
			device_updated = True

		if device_updated:
			device.save()

		return response.json()
	if response.status_code == 404:
		# {"error": "No information found about this instance id."}
		try:
			device = FCMDevice.objects.get(registration_id=registration_id)
		except FCMDevice.DoesNotExist:
			return response.json()
		if device.is_active:
			device.is_active = False
			device.save()
		return response.json()
	else:
		# raise appropriate RequestException
		response.raise_for_status()


@shared_task
def process_fcm_response(fcm_response, registration_ids):
	"""
	Subtask used to process the response from FCM after send notification/data messages.
	"""
	if fcm_response.get('failure') == 0 and fcm_response.get('canonical_ids') == 0:
		return True

	assert len(registration_ids) == len(fcm_response.get('results', []))

	if fcm_response.get('failure', 0) > 0 or fcm_response.get('canonical_ids', 0) > 0:
		for idx, registration_id in enumerate(registration_ids):
			# entries in fcm_response.results have the same order as registration_ids
			current_result = fcm_response.get('results', [])[idx]

			# canonical id received
			if current_result.get('registration_id'):
				FCMDevice.objects.filter(registration_id=registration_id)\
					.update(registration_id=current_result.get('registration_id'))

			# error for registration_id {error: NotRegistered}
			if current_result.get('error'):
				FCMDevice.objects.filter(registration_id=registration_id)\
					.update(is_active=False)
