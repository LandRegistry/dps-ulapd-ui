import unittest
import requests
import json
from unittest.mock import patch, Mock
from requests.exceptions import HTTPError, ConnectionError, Timeout
from ulapd_ui.main import app
from ulapd_ui.dependencies.ulapd_api import UlapdAPI
from ulapd_ui.exceptions import ApplicationError
from common_utilities import errors


def use_test_request_context(func):
    def run_with_context(*args, **kwargs):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                return func(*args, **kwargs)

    return run_with_context


class TestUlapdAPI(unittest.TestCase):
    def setUp(self):
        self.error_msg = 'Test error message'
        self.maxDiff = None

    @patch("requests.Session.get")
    @use_test_request_context
    def test_get_datasets(self, mock_get):
        mock_get.return_value.json.return_value = [{'name': 'ccod'}]
        mock_get.return_value.status_code = 200

        ulapd_api = UlapdAPI()
        response = ulapd_api.get_datasets()

        self.assertEqual(response, [{'name': 'ccod'}])

    @patch("requests.Session.get")
    @use_test_request_context
    def test_http_error(self, mock_get):
        error = ('ulapd_ui', 'API_HTTP_ERROR')
        response = Mock()
        response.status_code = 500
        response.raise_for_status.side_effect = HTTPError(self.error_msg)
        mock_get.return_value = response

        with self.assertRaises(ApplicationError) as cm:
            ulapd_api = UlapdAPI()
            ulapd_api.get_datasets()

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler=self.error_msg))
        self.assertEqual(cm.exception.code, errors.get_code(*error))
        self.assertEqual(cm.exception.http_code, 500)

    @patch("requests.Session.get")
    @use_test_request_context
    def test_connection_error(self, mock_get):
        error = ('ulapd_ui', 'API_CONN_ERROR')
        response = Mock()
        response.status_code = 500
        response.raise_for_status.side_effect = ConnectionError(self.error_msg)
        mock_get.return_value = response

        with self.assertRaises(ApplicationError) as cm:
            ulapd_api = UlapdAPI()
            ulapd_api.get_datasets()

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler=self.error_msg))
        self.assertEqual(cm.exception.code, errors.get_code(*error))
        self.assertEqual(cm.exception.http_code, 500)

    @patch("requests.Session.get")
    @use_test_request_context
    def test_timeout_error(self, mock_get):
        error = ('ulapd_ui', 'API_TIMEOUT')
        response = Mock()
        response.status_code = 500
        response.raise_for_status.side_effect = Timeout(self.error_msg)
        mock_get.return_value = response

        with self.assertRaises(ApplicationError) as cm:
            ulapd_api = UlapdAPI()
            ulapd_api.get_datasets()

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler=self.error_msg))
        self.assertEqual(cm.exception.code, errors.get_code(*error))
        self.assertEqual(cm.exception.http_code, 500)

    @patch("requests.Session.get")
    @use_test_request_context
    def test_get_external_datasets(self, mock_get):
        mock_get.return_value.json.return_value = [{'name': 'hpi'}]
        mock_get.return_value.status_code = 200

        ulapd_api = UlapdAPI()
        response = ulapd_api.get_external_datasets()

        self.assertEqual(response, [{'name': 'hpi'}])

    @patch("requests.Session.get")
    @use_test_request_context
    def test_get_dataset_by_name(self, mock_get):
        mock_get.return_value.json.return_value = {'name': 'ccod'}
        mock_get.return_value.status_code = 200

        ulapd_api = UlapdAPI()
        response = ulapd_api.get_dataset_by_name('ccod')

        self.assertEqual(response, {'name': 'ccod'})

    @patch("requests.Session.get")
    @use_test_request_context
    def test_get_dataset_history(self, mock_get):
        mock_get.return_value.json.return_value = {'name': 'ccod'}
        mock_get.return_value.status_code = 200

        ulapd_api = UlapdAPI()
        response = ulapd_api.get_dataset_history('ccod')

        self.assertEqual(response, {'name': 'ccod'})

    @patch("requests.Session.get")
    @use_test_request_context
    def test_get_download_link(self, mock_get):
        mock_get.return_value.json.return_value = {'link': 'https://s3.com'}
        mock_get.return_value.status_code = 200

        ulapd_api = UlapdAPI()
        response = ulapd_api.get_download_link('ccod', 'ccod_full.csv')

        self.assertEqual(response, {'link': 'https://s3.com'})

    @patch("requests.Session.get")
    @use_test_request_context
    def test_get_history_download_link(self, mock_get):
        mock_get.return_value.json.return_value = {'link': 'https://s3.com'}
        mock_get.return_value.status_code = 200

        ulapd_api = UlapdAPI()
        response = ulapd_api.get_history_download_link('ccod', 'ccod_full.csv', '07-19')

        self.assertEqual(response, {'link': 'https://s3.com'})

    @patch("requests.Session.get")
    @use_test_request_context
    def test_get_user_details(self, mock_get):
        mock_get.return_value.json.return_value = {'user_details': 'details'}
        mock_get.return_value.status_code = 200

        ulapd_api = UlapdAPI()
        response = ulapd_api.get_user_details('email', 'a@a.com')

        self.assertEqual(response, {'user_details': 'details'})

    @patch("requests.Session.get")
    @use_test_request_context
    def test_get_user_download_activity(self, mock_get):
        mock_get.return_value.json.return_value = [{'activity_id': 123}]
        mock_get.return_value.status_code = 200

        ulapd_api = UlapdAPI()
        response = ulapd_api.get_user_download_activity('43')

        self.assertEqual(response, [{'activity_id': 123}])

    @patch("requests.Session.post")
    @use_test_request_context
    def test_create_licence_agreement(self, mock_post):
        data = {"user_details_id": 1, "licence_id": "ccod"}
        mock_post.return_value.json.return_value = data
        mock_post.return_value.status_code = 201

        ulapd_api = UlapdAPI()
        response = ulapd_api.create_licence_agreement(data)

        self.assertEqual(response, data)
        args, kwargs = mock_post.call_args_list[0]
        self.assertEqual(kwargs['data'], json.dumps(data))

    @patch("requests.Session.post")
    @use_test_request_context
    def test_update_api_key(self, mock_post):
        mock_post.return_value.json.return_value = {'api_key': '1234'}
        mock_post.return_value.status_code = 201

        ulapd_api = UlapdAPI()
        response = ulapd_api.update_api_key('1')

        self.assertEqual(response, {'api_key': '1234'})
        args, kwargs = mock_post.call_args_list[0]
        self.assertEqual(kwargs['data'], json.dumps({}))

    @patch("requests.Session.post")
    @use_test_request_context
    def test_create_user(self, mock_post):
        data = {"email": "a@a.com", "name": "testy"}
        mock_post.return_value.json.return_value = data
        mock_post.return_value.status_code = 201

        ulapd_api = UlapdAPI()
        response = ulapd_api.create_user(data)

        self.assertEqual(response, data)
        args, kwargs = mock_post.call_args_list[0]
        self.assertEqual(kwargs['data'], json.dumps(data))

    @patch("requests.Session.post")
    @use_test_request_context
    def test_create_activity(self, mock_post):
        user_id = '1'
        activity_type = 'download'
        ip_address = '10.0.0.1'
        api = True
        file = 'ccod_full.csv'
        dataset_id = 'ccod'

        data = {
            'user_details_id': user_id,
            'activity_type': activity_type,
            'ip_address': ip_address,
            'api': api,
            'file': file,
            'dataset_id': dataset_id
        }

        mock_post.return_value.json.return_value = data
        mock_post.return_value.status_code = 201

        ulapd_api = UlapdAPI()
        response = ulapd_api.create_activity(user_id, activity_type, ip_address, api, file, dataset_id)

        self.assertEqual(response, data)
        args, kwargs = mock_post.call_args_list[0]
        self.assertEqual(kwargs['data'], json.dumps(data))
