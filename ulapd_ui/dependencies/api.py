from flask import current_app
import requests
from ulapd_ui.app import app


req = requests.Session()
req.headers.update({'Accept': 'application/json'})


def _conversion_table():
    return {
        '/api/authentication': app.config.get("AUTH_API_URL"),
        '/api/session': app.config.get("SESSION_API_URL"),
        '/api/account': app.config.get("ACCOUNT_API_URL"),
        '/api/notifications': app.config.get("NOTIFICATION_API_URL"),
        '/api/verification': app.config.get("VERIFICATION_API_URL")
    }


def _resolve_url(url):
    conversion_table = _conversion_table()
    for rule in conversion_table:
        new_url = url.replace(rule, conversion_table[rule])
        if url != new_url:
            return new_url
    return url


def _api_factory(method):
    def api_method(url, json=None, headers=None, external=False):
        try:
            if headers is None:
                headers = {}

            if not external:
                url = _resolve_url(url)

            current_app.logger.info('------------  API CALL START -------------')
            current_app.logger.info('API call to {}'.format(url))

            resp = None
            if json is None:
                resp = method(url, headers=headers)
            else:
                resp = method(url, json=json, headers=headers)

            status = resp.status_code
            current_app.logger.info('{} has returned status {}'.format(url, status))
            current_app.logger.info('------------  API CALL END -------------')
            try:
                json_resp = resp.json()
                return json_resp, status
            except ValueError:
                current_app.logger.debug('{} does not return json'.format(url))
                return {}, status
        except Exception as e:
            current_app.logger.debug('----------------------- Exception START --------------------------------')
            current_app.logger.exception(e)
            current_app.logger.debug('----------------------- Exception END ----------------------------------')
    return api_method


def api_get(url, headers=None, external=False):
    return _api_factory(req.get)(url, headers=headers, external=external)


def api_post(url, json=None, headers=None, external=False):
    return _api_factory(req.post)(url, json, headers, external)


def api_put(url, json=None, headers=None, external=False):
    return _api_factory(req.put)(url, json, headers, external)


def api_patch(url, json=None, headers=None, external=False):
    return _api_factory(req.patch)(url, json, headers, external)


def api_delete(url, json=None, headers=None, external=False):
    return _api_factory(req.delete)(url, json, headers, external)
