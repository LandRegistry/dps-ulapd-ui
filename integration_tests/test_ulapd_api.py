import unittest
import requests
from ulapd_ui.main import app


class TestUlapdAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.base_url = app.config.get('ULAPD_API_URL')

    def _get(self, route):
        headers = {'Accept': 'application/json'}
        url = '{}/{}'.format(self.base_url, route)
        return requests.get(url, headers=headers)

    def test_ulapd_api_health(self):
        resp = self._get('datasets')
        self.assertEqual(resp.status_code, 200)
