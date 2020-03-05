import unittest
from unittest.mock import patch, MagicMock

from ulapd_ui.dependencies.metric import send_metric, build_metric_data


class TestMetric(unittest.TestCase):

    def setUp(self):
        self.app_patcher = patch('ulapd_ui.dependencies.metric.app')
        mock_app = self.app_patcher.start()
        mock_app.config.get.return_value = '3'

    def tearDown(self):
        self.app_patcher.stop()

    @patch('ulapd_ui.dependencies.metric.current_app')
    @patch('ulapd_ui.dependencies.metric.metric_post')
    @patch('ulapd_ui.dependencies.metric.build_metric_data')
    def test_send_metric_dataset_event_ok(self, mock_build_data, mock_metric_post, *_):
        mock_build_data.return_value = {'foo': 'bar'}

        response = MagicMock()
        response.text = 'foobar'
        response.status_code = 200
        mock_metric_post.return_value = response

        send_metric('ccod', 'download', 'user_id', 'user_data', 'file_name')
        self.assertEqual(mock_build_data.call_count, 1)
        self.assertEqual(mock_metric_post.call_count, 1)

    @patch('ulapd_ui.dependencies.metric.current_app')
    @patch('ulapd_ui.dependencies.metric.metric_post')
    @patch('ulapd_ui.dependencies.metric.build_metric_data')
    def test_send_metric_dataset_event_retry(self, mock_build_data, mock_metric_post, *_):
        mock_build_data.return_value = {'foo': 'bar'}

        response = MagicMock()
        response.text = 'foobar'
        response.status_code = 400
        mock_metric_post.return_value = response

        send_metric('ccod', 'download', 'user_id', 'user_data', 'file_name')
        self.assertEqual(mock_build_data.call_count, 1)
        self.assertEqual(mock_metric_post.call_count, 3)

    @patch('ulapd_ui.dependencies.metric.build_metric_data')
    @patch('ulapd_ui.dependencies.metric.current_app')
    def test_send_metric_dataset_event_exception(self, mock_current_app, mock_build_data):
        mock_build_data.side_effect = Exception('error message')

        result = send_metric('ccod', 'download', 'user_id', 'user_data', 'file_name')
        self.assertEqual(mock_build_data.call_count, 1)
        self.assertEqual(mock_current_app.logger.error.call_count, 1)
        self.assertEqual(result, 'Failed')

    def test_build_metric_data_ok(self):
        user = MagicMock()
        user.email = 'test.tester@testemail.com'
        user_type = MagicMock()
        user_type.user_type = 'private-individual'
        user_details = MagicMock()
        user_details.first_name = 'test'
        user_details.last_name = 'tester'
        user_details.organisation_name = None
        user_details.city = 'Faketown'
        user_details.date_added = '2019-01-01 09:09:09'
        user_data = {
            'user': user,
            'user_details': user_details,
            'user_type': user_type,
            'contactable': True
        }

        result = build_metric_data('ccod', 'download', 'user_id', user_data, 'CCOD_FULL.zip')
        self.assertTrue('user' in result)
        self.assertTrue('activity' in result)
