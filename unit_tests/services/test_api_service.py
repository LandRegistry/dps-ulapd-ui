import unittest
from unittest.mock import patch, Mock
from ulapd_ui.exceptions import ApplicationError
import unit_tests.data.api_service_data as data
from ulapd_ui.services.api_service import (get_api_datasets,
                                           get_api_dataset_by_name,
                                           get_api_download_link,
                                           _authenticate)
from common_utilities import errors


class TestAPIService(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service._authenticate')
    def test_get_api_datasets(self, mock_auth, mock_ulapd_api):
        instance = mock_ulapd_api.return_value
        instance.get_datasets.return_value = data.get_datasets_return

        actual_output = get_api_datasets()
        expected_output = data.get_api_datasets_expected

        self.assertEqual(actual_output, expected_output)

    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service._authenticate')
    def test_get_api_datasets_not_found(self, mock_auth, mock_ulapd_api):
        error = ('ulapd_ui', 'NO_DATASETS_FOUND')
        instance = mock_ulapd_api.return_value
        instance.get_datasets.return_value = []

        with self.assertRaises(ApplicationError) as cm:
            get_api_datasets()

        self.assertEqual(cm.exception.message, errors.get_message(*error))
        self.assertEqual(cm.exception.code, errors.get_code(*error))

    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service._authenticate')
    def test_get_api_dataset_by_name(self, mock_auth, mock_ulapd_api):
        instance = mock_ulapd_api.return_value
        instance.get_dataset_by_name.return_value = {'name': 'ocod'}

        actual_output = get_api_dataset_by_name('ocod')
        expected_output = {
            "success": True,
            "result": {'name': 'ocod'}
        }

        self.assertEqual(actual_output, expected_output)

    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service._authenticate')
    def test_get_api_dataset_by_name_not_found(self, mock_auth, mock_ulapd_api):
        error = ('ulapd_ui', 'DATASET_NOT_FOUND')
        instance = mock_ulapd_api.return_value
        instance.get_dataset_by_name.return_value = None

        with self.assertRaises(ApplicationError) as cm:
            get_api_dataset_by_name('abc')

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler='abc'))
        self.assertEqual(cm.exception.code, errors.get_code(*error))

    @patch('ulapd_ui.services.api_service.send_metric')
    @patch('ulapd_ui.services.api_service.request')
    @patch('ulapd_ui.services.api_service.current_app')
    @patch('ulapd_ui.services.api_service._authenticate')
    @patch('ulapd_ui.services.api_service.UlapdAPI')
    def test_get_api_download_link(self, mock_ulapd_api, mock_auth, *_):
        instance = mock_ulapd_api.return_value
        instance.get_dataset_by_name.return_value = data.get_dataset_by_name['ocod']
        instance.get_download_link.return_value = {'link': 'https://S3-resource'}

        mock_auth.return_value = data.user_details_with_agreements

        actual_output = get_api_download_link('ocod', 'OCOD_FULL.CSV')
        expected_output = {
                "success": True,
                "result": {
                    "resource": 'OCOD_FULL.CSV',
                    "valid_for_seconds": 10,
                    "download_url": 'https://S3-resource'
                }
            }

        self.assertEqual(actual_output, expected_output)

    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service._authenticate')
    def test_get_api_download_link_not_agreed(self, mock_auth, mock_ulapd_api):
        error = ('ulapd_ui', 'NO_LICENCE_SIGNED')
        instance = mock_ulapd_api.return_value
        instance.get_dataset_by_name.return_value = data.get_dataset_by_name['ccod']

        mock_auth.return_value = data.user_details_no_agreements

        with self.assertRaises(ApplicationError) as cm:
            get_api_download_link('ccod', 'CCOD_FULL.CSV')

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler='ccod'))
        self.assertEqual(cm.exception.code, errors.get_code(*error))

    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service._authenticate')
    def test_get_api_download_link_not_agreed_private(self, mock_auth, mock_ulapd_api):
        error = ('ulapd_ui', 'NO_DATASET_ACCESS')
        instance = mock_ulapd_api.return_value
        instance.get_dataset_by_name.return_value = data.get_dataset_by_name['nps']

        mock_auth.return_value = data.user_details_no_agreements

        with self.assertRaises(ApplicationError) as cm:
            get_api_download_link('nps', 'NPS_FULL.CSV')

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler='nps'))
        self.assertEqual(cm.exception.code, errors.get_code(*error))

    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service._authenticate')
    def test_get_api_download_link_licence_not_valid(self, mock_auth, mock_ulapd_api):
        error = ('ulapd_ui', 'NO_LICENCE_SIGNED')
        instance = mock_ulapd_api.return_value
        instance.get_dataset_by_name.return_value = data.get_dataset_by_name['ccod']

        mock_auth.return_value = data.user_details_with_agreements

        with self.assertRaises(ApplicationError) as cm:
            get_api_download_link('ccod', 'CCOD_FULL.CSV')

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler='ccod'))
        self.assertEqual(cm.exception.code, errors.get_code(*error))

    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service._authenticate')
    @patch('ulapd_ui.services.api_service.current_app')
    def test_get_api_download_link_no_resource(self, mock_curr_app, mock_auth, mock_ulapd_api):
        error = ('ulapd_ui', 'FILE_DOES_NOT_EXIST')
        instance = mock_ulapd_api.return_value
        instance.get_dataset_by_name.return_value = data.get_dataset_by_name['ocod']

        mock_auth.return_value = data.user_details_with_agreements

        with self.assertRaises(ApplicationError) as cm:
            get_api_download_link('ocod', 'blah')

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler='blah'))
        self.assertEqual(cm.exception.code, errors.get_code(*error))

    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service._authenticate')
    @patch('ulapd_ui.services.api_service.current_app')
    def test_get_api_download_link_api_error(self, mock_curr_app, mock_auth, mock_ulapd_api):
        error = ('ulapd_ui', 'DATASET_NOT_FOUND')
        instance = mock_ulapd_api.return_value
        instance.get_dataset_by_name.return_value = data.get_dataset_by_name['ocod']
        instance.get_download_link.return_value = None

        mock_auth.return_value = data.user_details_with_agreements

        with self.assertRaises(ApplicationError) as cm:
            get_api_download_link('ocod', 'OCOD_FULL.CSV')

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler='ocod'))
        self.assertEqual(cm.exception.code, errors.get_code(*error))

    @patch('ulapd_ui.services.api_service.request')
    @patch('ulapd_ui.services.api_service.current_app')
    @patch('ulapd_ui.services.api_service._authenticate')
    @patch('ulapd_ui.services.api_service.UlapdAPI')
    @patch('ulapd_ui.services.api_service.send_metric')
    def test_get_api_download_link_generic_error(self, mock_metric, mock_ulapd_api, mock_auth, *_):
        instance = mock_ulapd_api.return_value
        instance.get_dataset_by_name.return_value = data.get_dataset_by_name['ocod']
        instance.get_download_link.return_value = {'link': 'https://S3-resource'}

        mock_auth.return_value = data.user_details_with_agreements

        mock_metric.side_effect = Exception('test')

        with self.assertRaises(Exception):
            get_api_download_link('ocod', 'OCOD_FULL.CSV')

    @patch('ulapd_ui.services.api_service.request')
    def test_authenticate(self, mock_request):
        m = Mock()
        m.get_user_details.return_value = {'user_details': 'happy'}

        actual_output = _authenticate(m)
        expected_output = {'user_details': 'happy'}

        self.assertEqual(actual_output, expected_output)

    @patch('ulapd_ui.services.api_service.request')
    def test_authenticate_fail(self, mock_request):
        error = ('ulapd_ui', 'API_KEY_ERROR')
        m = Mock()
        m.get_user_details.side_effect = ApplicationError('Test')

        mock_request.headers = {}
        mock_request.headers['Authorization'] = '1234'

        with self.assertRaises(ApplicationError) as cm:
            _authenticate(m)

        self.assertEqual(cm.exception.message, errors.get_message(*error, filler='1234'))
        self.assertEqual(cm.exception.code, errors.get_code(*error))
