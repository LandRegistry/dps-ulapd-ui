import unittest
from unittest.mock import patch, mock_open
import unit_tests.data.datasets_utilities_data as data
from unit_tests.data import rfi_dataset, rfi_expected_history, rfi_history
from ulapd_ui.utils.datasets_utilities import (accept_licence,
                                               check_agreement,
                                               historic_date_formatter,
                                               get_latest_download_activities,
                                               build_download_history,
                                               build_dataset_details,
                                               build_rfi_dataset_for_download)


class TestDatasetUtilities(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    # More for test coverage.
    @patch('ulapd_ui.utils.datasets_utilities.dps_session')
    @patch('ulapd_ui.utils.datasets_utilities.send_metric')
    @patch('ulapd_ui.utils.datasets_utilities.UlapdAPI')
    def test_accept_licence(self, mock_ulapd_api, mock_metric, mock_session):
        mock_session.get_state.return_value = data.session_data

        accept_licence(1)

        mock_metric.assert_called()

        licence_data = {
            'user_details_id': data.session_data['user']['user_details']['user_details_id'],
            'licence_id': 1
        }

        mock_ulapd_api.return_value.create_licence_agreement.assert_called_with(licence_data)

    @patch('ulapd_ui.utils.datasets_utilities.dps_session')
    @patch('ulapd_ui.utils.datasets_utilities.g')
    def test_check_agreement_valid(self, mock_g, mock_session):
        mock_session.get_state.return_value = data.session_data
        mock_g.user = 'a@fake.com'

        is_agreed = check_agreement('ccod')

        self.assertTrue(is_agreed)

    @patch('ulapd_ui.utils.datasets_utilities.dps_session')
    @patch('ulapd_ui.utils.datasets_utilities.g')
    def test_check_agreement_not_valid(self, mock_g, mock_session):
        mock_session.get_state.return_value = data.session_data
        mock_g.user = 'a@fake.com'

        is_agreed = check_agreement('ocod')

        self.assertFalse(is_agreed)

    @patch('ulapd_ui.utils.datasets_utilities.dps_session')
    @patch('ulapd_ui.utils.datasets_utilities.g')
    def test_check_agreement_no_session(self, mock_g, mock_session):
        mock_session.get_state.return_value = data.session_data
        mock_g.user = None

        is_agreed = check_agreement('ocod')

        self.assertFalse(is_agreed)

    def test_historic_date_formatter(self):
        # Test monthly formatting
        test_string = "May 2019"
        method_output = historic_date_formatter(test_string, 'Monthly')
        expected_output = "2019_05"
        self.assertEqual(expected_output, method_output)

        # Test daily formatting
        test_string = "02 May 2019"
        method_output = historic_date_formatter(test_string, 'Daily')
        expected_output = "2019_05_02"
        self.assertEqual(expected_output, method_output)

    def test_get_latest_download_activities(self):
        input = data.get_latest_download_activities_input
        expected_output = data.get_latest_download_activities_expected

        actual_output = get_latest_download_activities(input)

        self.assertCountEqual(actual_output, expected_output)

    @patch('ulapd_ui.utils.datasets_utilities.dps_session')
    @patch('ulapd_ui.utils.datasets_utilities.g')
    @patch('ulapd_ui.utils.datasets_utilities.UlapdAPI')
    @patch('ulapd_ui.utils.datasets_utilities.get_latest_download_activities')
    @patch('ulapd_ui.utils.datasets_utilities.current_app')
    @patch('ulapd_ui.utils.datasets_utilities.check_agreement')
    def test_build_download_history(self, mock_check, mock_c_app, mock_get_latest, mock_ulapd_api, mock_g, mock_sess):
        mock_sess.get_state.return_value = data.session_data
        mock_get_latest.return_value = data.build_download_history_activites
        mock_g.user = 'a@a.com'
        mock_ulapd_api.return_value.get_dataset_by_name.side_effect = _get_dataset_by_name
        mock_check.return_value = True

        actual_output = build_download_history()
        expected_output = data.build_download_history_expected

        self.assertEqual(actual_output, expected_output)

    def test_build_dataset_details_full(self):
        actual_output = build_dataset_details('ocod', False)
        self.assertEqual(actual_output, {})

    @patch('ulapd_ui.utils.datasets_utilities.json')
    def test_build_dataset_details(self, mock_json):
        with patch('builtins.open', mock_open(read_data='Hello World')):
            mock_json.loads.return_value = {
                'example_data': [
                    {
                        'data': 'Title number',
                        'meaning': 'Number used by HM Land Registry to identify the land and landowner',
                        'examples': [
                            'ZZ1234'
                        ]
                    }
                ]
            }

            expected_output = {
                'example_data': [{
                        'data': 'Title number',
                        'meaning': 'Number used by HM Land Registry to identify the land and landowner',
                        'examples': [
                            'ZZ1234'
                        ]
                    }],
            }

            actual_output = build_dataset_details('ocod')
            self.assertEqual(actual_output, expected_output)

    def test_build_rfi_dataset_for_download(self):
        dataset, history = build_rfi_dataset_for_download(rfi_dataset.dataset, rfi_history.history)
        self.assertEqual(history, rfi_expected_history.expected_history)


# Helpers
def _get_dataset_by_name(id):
    datasets = {
        'ocod': {
            'title': 'ocod',
            'resources': [],
            'licence_id': 'ocod',
            'last_updated': '07 November 2019'
        },
        'ccod': {
            'title': 'ccod',
            'resources': [],
            'licence_id': 'ccod',
            'last_updated': '30 November 2019'
        },
        'nps': {
            'title': 'nps',
            'resources': [],
            'licence_id': None,
            'last_updated': '30 November 2019'
        }
    }

    return datasets[id]
