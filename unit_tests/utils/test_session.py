import unittest
from unittest.mock import patch
from flask import Response
from ulapd_ui.utils.session import dps_session


class TestSession(unittest.TestCase):

    @patch('ulapd_ui.utils.session.current_app')
    @patch('ulapd_ui.utils.session.api_get')
    @patch('ulapd_ui.utils.session.dps_session.destroy')
    @patch('ulapd_ui.utils.session.request')
    def test_is_valid_return_true(self, mock_request, mock_destroy, mock_api_get, *_):
        mock_request.cookies = {'AccessToken': '123'}
        response = Response()
        mock_api_get.return_value = response, 204

        result = dps_session().is_valid()

        self.assertEqual(mock_destroy.call_count, 0)
        self.assertEqual(mock_api_get.call_count, 1)
        self.assertEqual(result, True)

    @patch('ulapd_ui.utils.session.current_app')
    @patch('ulapd_ui.utils.session.api_get')
    @patch('ulapd_ui.utils.session.dps_session.destroy')
    @patch('ulapd_ui.utils.session.request')
    def test_is_valid_wrong_status_code_return_false(self, mock_request, mock_destroy, mock_api_get, *_):
        mock_request.cookies = {'AccessToken': '123'}
        response = Response()
        mock_api_get.return_value = response, 500

        result = dps_session().is_valid()

        self.assertEqual(mock_destroy.call_count, 1)
        self.assertEqual(mock_api_get.call_count, 1)
        self.assertEqual(result, False)

    @patch('ulapd_ui.utils.session.dps_session.destroy')
    @patch('ulapd_ui.utils.session.request')
    def test_is_valid_no_access_token_return_false(self, mock_request, mock_destroy):
        mock_request.cookies = {'key': 'value'}

        result = dps_session().is_valid()

        self.assertEqual(mock_destroy.call_count, 1)
        self.assertEqual(result, False)

    @patch('ulapd_ui.utils.session.current_app')
    @patch('ulapd_ui.utils.session.api_get')
    @patch('ulapd_ui.utils.session.dps_session.destroy')
    @patch('ulapd_ui.utils.session.session')
    @patch('ulapd_ui.utils.session.request')
    def test_populate_state_returns_dps_session(self, mock_request, mock_session, mock_destroy, mock_api_get, *_):
        mock_request.cookies = {'AccessToken': '123'}

        response = Response()
        response.status_code = 200
        response.text = {"session": "content"}
        mock_api_get.return_value = response.text, response.status_code

        result = dps_session().populate_state({'dps-session': {}})

        self.assertEqual(mock_destroy.call_count, 0)
        self.assertEqual(mock_api_get.call_count, 1)
        self.assertEqual(result, response.text)

    @patch('ulapd_ui.utils.session.current_app')
    @patch('ulapd_ui.utils.session.api_get')
    @patch('ulapd_ui.utils.session.dps_session.destroy')
    @patch('ulapd_ui.utils.session.session')
    @patch('ulapd_ui.utils.session.request')
    def test_populate_state_500_response_returns_empty_object(self, mock_request, mock_session,
                                                              mock_destroy, mock_api_get, *_):
        mock_request.cookies = {'AccessToken': '123'}

        response = Response()
        response.status_code = 500
        mock_api_get.return_value = response, response.status_code

        result = dps_session().populate_state({'dps-session': {}})

        self.assertEqual(mock_destroy.call_count, 1)
        self.assertEqual(mock_api_get.call_count, 1)
        self.assertEqual(result, {})

    @patch('ulapd_ui.utils.session.dps_session.destroy')
    @patch('ulapd_ui.utils.session.request')
    def test_populate_state_no_access_token_returns_empty_object(self, mock_request, mock_destroy):
        mock_request.cookies = {}

        result = dps_session().populate_state({'dps-session': {}})

        self.assertEqual(mock_destroy.call_count, 1)
        self.assertEqual(result, {})

    @patch('ulapd_ui.utils.session.session')
    def test_get_state_returns_dps_session(self, mock_session):
        mock_session.__contains__.return_value = True
        mock_session.__getitem__.return_value = 'state'

        result = dps_session().get_state()

        self.assertEqual(result, 'state')

    @patch('ulapd_ui.utils.session.session')
    def test_get_state_returns_empty_object(self, mock_session):
        mock_session.__contains__.return_value = False

        result = dps_session().get_state()

        self.assertEqual(result, {})

    @patch('ulapd_ui.utils.session.session')
    @patch('ulapd_ui.utils.session.dps_session.is_valid')
    def test_is_set_return_true(self, mock_is_valid, mock_session):
        mock_is_valid.return_value = True
        s = {'dps-session': 'true'}
        mock_session.__contains__.side_effect = s.__contains__

        result = dps_session().is_set()

        self.assertEqual(result, True)

    @patch('ulapd_ui.utils.session.session')
    @patch('ulapd_ui.utils.session.dps_session.is_valid')
    def test_is_set_return_false(self, mock_is_valid, mock_session):
        mock_is_valid.return_value = True
        s = {}
        mock_session.__contains__.side_effect = s.__contains__

        result = dps_session().is_set()

        self.assertEqual(result, False)

    @patch('ulapd_ui.utils.session.dps_session.is_valid')
    def test_is_set_return_false_session_not_valid(self, mock_is_valid):
        mock_is_valid.return_value = False
        result = dps_session().is_set()

        self.assertEqual(result, False)

    @patch('ulapd_ui.utils.session.session')
    @patch('ulapd_ui.utils.session.dps_session.is_set')
    def test_is_logged_in_return_true(self, mock_is_set, mock_session):
        mock_is_set.return_value = True
        mock_session.__getitem__.return_value = {'user': 'true'}

        result = dps_session().is_logged_in()

        self.assertEqual(result, True)

    @patch('ulapd_ui.utils.session.session')
    @patch('ulapd_ui.utils.session.dps_session.is_set')
    def test_is_logged_in_return_false(self, mock_is_set, mock_session):
        mock_is_set.return_value = True
        mock_session.__getitem__.return_value = {'no_user': {}}

        result = dps_session().is_logged_in()

        self.assertEqual(result, False)

    @patch('ulapd_ui.utils.session.dps_session.is_set')
    def test_is_logged_in_return_false_session_not_set(self, mock_is_set):
        mock_is_set.return_value = False

        result = dps_session().is_logged_in()

        self.assertEqual(result, False)

    @patch('ulapd_ui.utils.session.current_app')
    @patch('ulapd_ui.utils.session.session')
    @patch('ulapd_ui.utils.session.api_put')
    @patch('ulapd_ui.utils.session.request')
    @patch('ulapd_ui.utils.session.dps_session.is_valid')
    def test_commit_ok(self, mock_is_valid, mock_request, mock_api_put, mock_session, mock_curr_app):
        mock_request.cookies = {'AccessToken': '123'}
        mock_is_valid.return_value = True
        response = Response()
        mock_api_put.return_value = response, 200

        mock_session.__getitem__.return_value = {'session': 'committed'}

        dps_session().commit()

        mock_curr_app.logger.info.assert_called_with('Updating new session state for:123')
        mock_curr_app.logger.error.assert_not_called()
        self.assertEqual(mock_api_put.call_count, 1)
        mock_api_put.assert_called_with('/api/session/123/state', json={'session': 'committed'},
                                        headers={'Content-Type': 'application/json'})

    @patch('ulapd_ui.utils.session.current_app')
    @patch('ulapd_ui.utils.session.session')
    @patch('ulapd_ui.utils.session.api_put')
    @patch('ulapd_ui.utils.session.request')
    @patch('ulapd_ui.utils.session.dps_session.is_valid')
    def test_commit_log_error_status_500(self, mock_is_valid, mock_request, mock_api_put, mock_session, mock_curr_app):
        mock_request.cookies = {'AccessToken': '123'}
        mock_is_valid.return_value = True
        response = Response()
        mock_api_put.return_value = response, 500

        mock_session.__getitem__.return_value = {'session': 'committed'}

        dps_session().commit()

        mock_curr_app.logger.info.assert_called_with('Updating new session state for:123')
        mock_curr_app.logger.error.assert_called_with('A problem happened with committing the session')
        self.assertEqual(mock_api_put.call_count, 1)
        mock_api_put.assert_called_with('/api/session/123/state', json={'session': 'committed'},
                                        headers={'Content-Type': 'application/json'})

    @patch('ulapd_ui.utils.session.current_app')
    @patch('ulapd_ui.utils.session.api_put')
    @patch('ulapd_ui.utils.session.request')
    @patch('ulapd_ui.utils.session.dps_session.is_valid')
    def test_commit_session_not_valid(self, mock_is_valid, mock_request, mock_api_put, mock_curr_app):
        mock_request.cookies = {'AccessToken': '123'}
        mock_is_valid.return_value = False

        dps_session().commit()

        mock_curr_app.logger.info.assert_not_called()
        mock_curr_app.logger.error.assert_not_called()
        mock_api_put.assert_not_called()
