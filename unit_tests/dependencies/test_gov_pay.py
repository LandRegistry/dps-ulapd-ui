import unittest
from unittest.mock import patch
from ulapd_ui.dependencies.gov_pay import request_payment


class TestGovPay(unittest.TestCase):

    def setUp(self):
        self.amount = 0
        self.reference = 'HMLR Data Publication'
        self.description = 'Data Publication Service verification'
        self.user_type = 'personal'

    @patch('ulapd_ui.dependencies.gov_pay.api_post')
    @patch('ulapd_ui.dependencies.gov_pay.url_for')
    @patch('ulapd_ui.dependencies.gov_pay._make_headers')
    @patch('ulapd_ui.dependencies.gov_pay.current_app')
    def test_request_payment_ok(self, mock_curr_app, mock_headers, mock_url_for, mock_post):
        mock_post.return_value = ({'govpay': 'stuff'}, 201)
        mock_url_for.return_value = '/some_url'
        result = request_payment(self.amount, self.reference, self.description, self.user_type)
        self.assertEqual(result, {'govpay': 'stuff'})
        self.assertEqual(mock_headers.call_count, 1)

    @patch('ulapd_ui.dependencies.gov_pay.api_post')
    @patch('ulapd_ui.dependencies.gov_pay.url_for')
    @patch('ulapd_ui.dependencies.gov_pay._make_headers')
    @patch('ulapd_ui.dependencies.gov_pay.current_app')
    def test_request_payment_fail(self, mock_curr_app, mock_headers, mock_url_for, mock_post):
        mock_post.return_value = ({'govpay': 'stuff'}, 500)
        mock_url_for.return_value = '/some_url'
        result = request_payment(self.amount, self.reference, self.description, self.user_type)
        self.assertEqual(mock_headers.call_count, 1)
        self.assertEqual(mock_curr_app.logger.error.call_count, 1)
        self.assertEqual(result, None)
