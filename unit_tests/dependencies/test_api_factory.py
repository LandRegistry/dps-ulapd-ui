import unittest
from unittest.mock import patch
from ulapd_ui.dependencies.api import api_get, api_post, api_delete, api_put, api_patch, _resolve_url


class TestApiDependency(unittest.TestCase):

    def setUp(self):
        self.app_patcher = patch('ulapd_ui.dependencies.api.app')
        mock_app = self.app_patcher.start()
        mock_app.config.get.return_value = 'http://test:8080'

        self.curr_app_patcher = patch('ulapd_ui.dependencies.api.current_app')
        self.curr_app_patcher.start()

    def tearDown(self):
        self.app_patcher.stop()
        self.curr_app_patcher.stop()

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_get_ok(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 200
        response.json.return_value = {'key': 'value'}
        mock_req.get.return_value = response

        test_response, test_code = api_get('/url')

        self.assertEqual(test_response, {'key': 'value'})
        self.assertEqual(test_code, 200)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_get_fail_status_code_500(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 500
        response.json.return_value = {}
        mock_req.get.return_value = response

        test_response, test_code = api_get('/url')

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 500)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_get_fail_status_code_401_not_authorized(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 401
        response.json.return_value = {}
        mock_req.get.return_value = response

        test_response, test_code = api_get('/url')

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 401)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_get_fail_value_error(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 205
        response.json.side_effect = ValueError
        mock_req.get.return_value = response

        test_response, test_code = api_get('/url')

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 205)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_post_ok(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 200
        response.json.return_value = {'post': 'true'}
        mock_req.post.return_value = response

        test_response, test_code = api_post('url', {'post': 'true'})

        self.assertEqual(test_response, {'post': 'true'})
        self.assertEqual(test_code, 200)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_post_fail_status_code_500(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 500
        response.json.return_value = {}
        mock_req.post.return_value = response

        test_response, test_code = api_post('/url', {'post': 'true'})

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 500)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_post_fail_status_code_401_not_authorized(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 401
        response.json.return_value = {}
        mock_req.post.return_value = response

        test_response, test_code = api_post('/url')

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 401)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_post_fail_value_error(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 205
        response.json.side_effect = ValueError
        mock_req.post.return_value = response

        test_response, test_code = api_post('/url', {'post': 'true'})

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 205)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_put_ok(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 200
        response.json.return_value = {'put': 'true'}
        mock_req.put.return_value = response

        test_response, test_code = api_put('/url', {'put': 'true'})

        self.assertEqual(test_response, {'put': 'true'})
        self.assertEqual(test_code, 200)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_put_fail_status_code_500(self, mock_req,  mock_requests):
        response = mock_requests.Response()
        response.status_code = 500
        response.json.return_value = {}
        mock_req.put.return_value = response

        test_response, test_code = api_put('/url', {'put': 'true'})

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 500)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_put_fail_status_code_401_not_authorized(self, mock_req,  mock_requests):
        response = mock_requests.Response()
        response.status_code = 401
        response.json.return_value = {}
        mock_req.put.return_value = response

        test_response, test_code = api_put('/url')

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 401)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_put_fail_value_error(self, mock_req,  mock_requests):
        response = mock_requests.Response()
        response.status_code = 205
        response.json.side_effect = ValueError
        mock_req.put.return_value = response

        test_response, test_code = api_put('/url', {'put': 'true'})

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 205)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_patch_ok(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 200
        response.json.return_value = {'patch': 'true'}
        mock_req.patch.return_value = response

        test_response, test_code = api_patch('/url', {'patch': 'true'})

        self.assertEqual(test_response, {'patch': 'true'})
        self.assertEqual(test_code, 200)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_patch_fail_status_code_500(self, mock_req,  mock_requests):
        response = mock_requests.Response()
        response.status_code = 500
        response.json.return_value = {}
        mock_req.patch.return_value = response

        test_response, test_code = api_patch('/url', {'patch': 'true'})

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 500)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_patch_fail_status_code_401_not_authorized(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 401
        response.json.return_value = {}
        mock_req.patch.return_value = response

        test_response, test_code = api_patch('/url')

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 401)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_patch_fail_value_error(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 205
        response.json.side_effect = ValueError
        mock_req.patch.return_value = response

        test_response, test_code = api_patch('/url', {'patch': 'true'})

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 205)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_delete_ok(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 200
        response.json.return_value = {'patch': 'true'}
        mock_req.delete.return_value = response

        test_response, test_code = api_delete('/url', {'patch': 'true'})

        self.assertEqual(test_response, {'patch': 'true'})
        self.assertEqual(test_code, 200)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_delete_fail_status_code_500(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 500
        response.json.return_value = {}
        mock_req.delete.return_value = response

        test_response, test_code = api_delete('/url', {'patch': 'true'})

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 500)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_delete_fail_status_code_401_not_authorized(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 401
        response.json.return_value = {}
        mock_req.delete.return_value = response

        test_response, test_code = api_delete('/url')

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 401)

    @patch('ulapd_ui.dependencies.api.requests')
    @patch('ulapd_ui.dependencies.api.req')
    def test_api_delete_fail_value_error(self, mock_req, mock_requests):
        response = mock_requests.Response()
        response.status_code = 205
        response.json.side_effect = ValueError
        mock_req.delete.return_value = response

        test_response, test_code = api_delete('/url', {'patch': 'true'})

        self.assertEqual(test_response, {})
        self.assertEqual(test_code, 205)

    def test_resolve_url_pass(self):
        relative_url = '/api/authentication/v1/test'
        absolute_url = _resolve_url(relative_url)

        self.assertEqual(absolute_url, 'http://test:8080/v1/test')

    def test_resolve_url_skip(self):

        relative_url = 'http://external/api/test'
        absolute_url = _resolve_url(relative_url)

        self.assertEqual(absolute_url, relative_url)
