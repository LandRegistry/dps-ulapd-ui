import unittest
import requests
from ulapd_ui.main import app


class TestMetricAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = app.config.get('METRIC_API_URL')

    def _get(self, route):
        headers = {'Accept': 'application/json'}
        url = '{}{}'.format(self.base_url, route)
        return requests.get(url, headers=headers)

    def test_metric_api_health(self):
        resp = self._get('')
        self.assertEqual(resp.status_code, 200)
