import unittest
from unittest.mock import patch
from ulapd_ui.views.password import handle_expired_link


class TestPassword(unittest.TestCase):

    @patch('ulapd_ui.views.password.api_get')
    @patch('ulapd_ui.views.password.api_post')
    @patch('ulapd_ui.views.password.current_app')
    def test_handle_expired_link_ok(self, mock_curr_app, mock_post, mock_get):
        mock_get.return_value = ({'sub': '123-232-3232'}, 200)
        mock_post.return_value = ({}, 201)

        result = handle_expired_link('12345')
        self.assertEqual(result, True)

    @patch('ulapd_ui.views.password.api_get')
    @patch('ulapd_ui.views.password.current_app')
    def test_handle_expired_link_get_failed(self, mock_curr_app, mock_get):
        mock_get.return_value = ('Decode error', 500)

        result = handle_expired_link('12345')
        self.assertEqual(result, False)
        mock_curr_app.logger.error.assert_called_with('Error decoding the jwt: Decode error')

    @patch('ulapd_ui.views.password.api_get')
    @patch('ulapd_ui.views.password.api_post')
    @patch('ulapd_ui.views.password.current_app')
    def test_handle_expired_link_post_failed(self, mock_curr_app, mock_post, mock_get):
        mock_get.return_value = ({'sub': '123-232-3232'}, 200)
        mock_post.return_value = ('Activation error', 500)

        result = handle_expired_link('12345')
        self.assertEqual(result, False)
        mock_curr_app.logger.error.assert_called_with('Error activating the users account: Activation error')
