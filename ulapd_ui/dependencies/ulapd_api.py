import requests
import json
from flask import current_app, g
from ulapd_ui.exceptions import ApplicationError
from common_utilities import errors


class UlapdAPI(object):
    def __init__(self):
        self.base_url = current_app.config['ULAPD_API_URL']

    def _request(self, uri, data=None):
        url = '{}/{}'.format(self.base_url, uri)
        headers = {'Accept': 'application/json'}
        timeout = current_app.config['DEFAULT_TIMEOUT']

        try:
            if data is None:
                response = g.requests.get(url, headers=headers, timeout=timeout)
            else:
                headers['Content-Type'] = 'application/json'
                response = g.requests.post(url, headers=headers, timeout=timeout, data=data)

            status = response.status_code
            if status == 204:
                return {}
            if status == 404:
                raise ApplicationError(*errors.get('ulapd_ui', 'RESOURCE_NOT_FOUND', filler=uri), http_code=status)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            raise ApplicationError(*errors.get('ulapd_ui', 'API_HTTP_ERROR', filler=e), http_code=status)
        except requests.exceptions.ConnectionError as e:
            raise ApplicationError(*errors.get('ulapd_ui', 'API_CONN_ERROR', filler=e), http_code=status)
        except requests.exceptions.Timeout as e:
            raise ApplicationError(*errors.get('ulapd_ui', 'API_TIMEOUT', filler=e), http_code=status)

    def get_datasets(self):
        current_app.logger.info('Getting list of datasets...')
        return self._request(uri='datasets')

    def get_external_datasets(self):
        current_app.logger.info('Getting list of external datasets...')
        return self._request(uri='datasets?external=true')

    def get_dataset_by_name(self, name):
        current_app.logger.info('Getting dataset: {}'.format(name))
        return self._request(uri='datasets/{}'.format(name))

    def get_dataset_history(self, name):
        current_app.logger.info('Getting dataset history: {}'.format(name))
        return self._request(uri='datasets/{}/history'.format(name))

    def get_download_link(self, dataset_name, file):
        current_app.logger.info('Getting download link for dataset: {} - file: {}'.format(dataset_name, file))
        return self._request(uri='datasets/download/{}/{}'.format(dataset_name, file))

    def get_history_download_link(self, dataset_name, file, date):
        current_app.logger.info('Getting history download link for dataset: {} - file: {} - date: {}'.format(
                                dataset_name, file, date))
        return self._request(uri='datasets/download/history/{}/{}/{}'.format(dataset_name, file, date))

    def get_user_details(self, key_type, key):
        current_app.logger.info('Getting user details for: {}: {}'.format(key_type, key))
        return self._request(uri='users/{}/{}'.format(key_type, key))

    def get_user_download_activity(self, user_id):
        current_app.logger.info('Getting user {} download'.format(user_id))
        return self._request(uri='activities/{}'.format(user_id))

    def create_licence_agreement(self, data):
        current_app.logger.info('Agreeing {} licence for user {}'.format(data['licence_id'], data['user_details_id']))
        return self._request(uri='users/licence', data=json.dumps(data))

    def update_api_key(self, user_id):
        current_app.logger.info('Resetting API key for user: {}'.format(user_id))
        return self._request(uri='users/{}/update_api_key'.format(user_id), data=json.dumps({}))

    def create_user(self, payload):
        current_app.logger.info('Creating user: {}'.format(payload['email']))
        return self._request(uri='users', data=json.dumps(payload))

    def create_activity(self, user_details_id, activity_type, ip_address, api, file, dataset_id):
        data = json.dumps({
            'user_details_id': user_details_id,
            'activity_type': activity_type,
            'ip_address': ip_address,
            'api': api,
            'file': file,
            'dataset_id': dataset_id
        })
        current_app.logger.info('Creating activity {}'.format(data))
        return self._request(uri='activities', data=data)
