from flask import url_for, current_app
from ulapd_ui.dependencies.api import api_post, api_get
from ulapd_ui.app import app

gov_pay_url = app.config.get("GOVPAY_URL")

# class GovPayService(object):
#     """Service class for making requests to GovPay."""


def request_payment(amount, reference, description, user_type):
    if user_type == 'personal':
        return_url = app.config.get("SITE_URL") + url_for('registration_personal.handle_verification')
    else:
        return_url = app.config.get("SITE_URL") + \
            url_for('registration_overseas_org.handle_verification_overseas')
    body = {
        'amount': amount,
        'reference': reference,
        'description': description,
        'return_url': return_url
    }

    current_app.logger.info('Requesting GovPay payment with reference {}'.format(reference))
    response, status_code = api_post(gov_pay_url, json=body, headers=_make_headers(), external=True)
    if status_code != 201:
        current_app.logger.error('Fail response from GovPay API: {}'.format(response))
        return None
    else:
        return response


def get_payment_status(payment_id):
    current_app.logger.info('Finding GovPay payment with id {}'.format(payment_id))
    response, status_code = api_get(gov_pay_url + "/" + payment_id, headers=_make_headers(), external=True)

    if status_code != 200:
        current_app.logger.error("Fail response from GovPay API: {}".format(response))
        return None
    else:
        return response


def _make_headers():
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + app.config.get("GOVPAY_API_KEY")
    }

    return headers
