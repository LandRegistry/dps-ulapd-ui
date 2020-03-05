from flask import current_app, request, make_response, Blueprint, render_template, url_for, redirect
from ulapd_ui.utils.validation import FormValidator, is_not_empty, password_length, email_validator, \
    password_letters, password_number, password_symbol, confirm_passwords_match, ValidationResult
from ulapd_ui.utils.session import dps_session
from ulapd_ui.dependencies.api import api_post, api_get, api_patch

password = Blueprint('password', __name__, url_prefix='/password')


@password.route("")
def redirect_to_reset():
    return redirect(url_for('.get_password_reset'))


@password.route("/reset", methods=['GET'])
def get_password_reset():
    return render_template('app/password/reset.html')


@password.route("/reset", methods=['POST'])
def post_password_reset():
    try:
        email = request.form['email']
        json_resp, status = api_post('/api/authentication/token',
                                     json={"email": email})

        form = FormValidator('An error has occurred')
        form.add_validator('email', email, [email_validator, is_not_empty], empty_msg='Enter your email address')

        if status != 200 or not form.is_valid():
            raise ValueError

        token = json_resp['token']
        decoded_jwt, status = api_get('/api/authentication/token/' +
                                      token +
                                      '?validation-type=reset-password')

        if status != 200:
            current_app.logger.error('Token has failed validation:' + decoded_jwt['error'])
            raise ValueError

        first_name = decoded_jwt['principle']['first_name']
        url = current_app.config.get("SITE_URL") + "/password/change?t=" + token
        current_app.logger.info(url)

        template_id = current_app.config.get("RESET_PASSWORD_TEMPLATE")
        _, email_status = api_post('/api/notifications', json={
                "email_address": email,
                "template_id": template_id,
                "personalisation": {
                    "first_name": first_name,
                    "last_name": decoded_jwt['principle']['surname'],
                    "change_password_link": url
                },
                "reference": "password-reset"
            },
            headers={'Accept': 'application/json'}
        )
        if email_status != 201:
            raise ValueError

        return render_template('app/password/email_sent.html', email=email)

    except ValueError:
        form = FormValidator('An error has occurred')
        form.add_validator('email', email, [is_not_empty, email_validator], empty_msg='Enter your email address')
        return render_template('app/password/reset.html',
                               error_title="There was a problem",
                               fields=form.validate(),
                               )


def password_token_is_valid(token):
    decoded_jwt, status = api_get('/api/authentication/token/' +
                                  token +
                                  '?validation-type=reset-password')

    if status == 200:
        return decoded_jwt, True
    else:
        return {}, False


def handle_password_create(action):
    try:
        token = request.args['t']
        if password_token_is_valid(token)[1]:
            return render_template('app/password/change.html', token=token, action=action)
        else:
            raise KeyError

    except Exception:
        current_app.logger.error('Can not validate JSON Web Token - Signature has expired')
        return render_template(
            'app/error.html',
            title="The link to create your password has expired",
            link={
                'text': 'Send a new link',
                'href': 'password/expired_link?t={}'.format(token)
            }
        )


@password.route("/create", methods=['GET'])
def get_password_create():
    return handle_password_create('create')


@password.route("/change", methods=['GET'])
def get_password_change():
    return handle_password_create('change')


@password.route("/expired_link", methods=['GET'])
def expired_link():
    try:
        token = request.args['t']
        if handle_expired_link(token):
            return render_template('activation_resent.html')
        else:
            raise KeyError
    except Exception as e:
        current_app.logger.error(e)
        raise Exception('Error while resending activation link after expiry')


def handle_expired_link(token):
    try:
        current_app.logger.info('resetting expired link for token: {}'.format(token))

        decoded_jwt, status = api_get('/api/authentication/token/' +
                                      token +
                                      '?validation-type=expired-token')

        if status != 200:
            current_app.logger.error('Error decoding the jwt: {}'.format(decoded_jwt))
            return False

        api_url = '/api/account/users/{}/activate'.format(decoded_jwt['sub'])
        resp, code = api_post(api_url, headers={'Content-Type': 'application/json'})

        if code < 299:
            return True
        else:
            current_app.logger.error('Error activating the users account: {}'.format(resp))
            return False
    except Exception as e:
        current_app.logger.error(e)
        return False


def _validate_and_save_password(user_id, password, confirm_password):
    try:
        form = FormValidator('Enter a valid password')
        form.add_validator('passwords',
                           password,
                           fvs=[password_length, password_letters, password_number, password_symbol])
        form.add_validator('confirm_password',
                           [password, confirm_password],
                           fvs=confirm_passwords_match)

        if not form.is_valid():
            current_app.logger.error('New password has failed validation')
            raise ValueError

        _, status = api_patch(
            '/api/account/users/' + user_id,
            json={'password': password, 'disabled': None},
            headers={'Content-Type': 'application/merge-patch+json'})

        if status != 204:
            current_app.logger.error('Account-api has failed the validation')
            raise ValueError

        return True, {}

    except ValueError as e:
        current_app.logger.error(e)
        result = form.validate()
        if (not result['passwords'].error) and (not result['confirm_password'].error):
            result = {
                'passwords': ValidationResult(0,
                                              None,
                                              ['Enter a valid password'])
            }
        return False, result


def _send_confirmation_email(template_id, email, personalisation, reference):
    body, _ = api_post('/api/notifications', json={
            "email_address": email,
            "template_id": template_id,
            "personalisation": personalisation,
            "reference": reference
        },
        headers={'Accept': 'application/json'}
    )
    current_app.logger.info(body)


@password.route("/create", methods=['POST'])
def post_password_create():
    return handle_change_password('create', 'REGISTRATION_COMPLETE_TEMPLATE')


@password.route("/change", methods=['POST'])
def post_password_change():
    return handle_change_password('change', 'PASSWORD_CHANGED_TEMPLATE')


def handle_change_password(route, template):
    try:
        token = request.form['t']
        decoded_jwt, is_token_valid = password_token_is_valid(token)
        if not is_token_valid:
            current_app.logger.error('Token has failed validation:' + decoded_jwt['error'])
            raise KeyError

        password = request.form['password']
        confirm_password = request.form['confirm_password']

        user_id = decoded_jwt['sub']
        is_form_valid, result = _validate_and_save_password(user_id, password, confirm_password)
        if not is_form_valid:
            return render_template(
                'app/password/change.html',
                error_title="There is a problem",
                fields=result,
                token=token,
                action=route
            )

        title_msg = "Your password has been reset" if route == 'change' else "Your password has been created"
        resp = make_response(
            render_template('app/confirmation/index.html',
                            title=title_msg,
                            what_is_next=[
                                "You can now sign in using your new password.\
                                <br/><a class='govuk-link' href='/sign-in'>Sign in</a>"
                            ]))

        # Destroy the session if the user was logged in
        # but has changed his password
        if dps_session.is_logged_in():
            dps_session.destroy()
            resp.set_cookie('AccessToken', '', expires=0)

        template_id = current_app.config.get(template)
        user = decoded_jwt['principle']
        login_url = current_app.config.get("SITE_URL") + '/sign-in'
        _send_confirmation_email(template_id, user['email'], {
            "first_name": user['first_name'],
            "last_name": user['surname'],
            "login_link": login_url
        }, 'password-changed')
        return resp

    except KeyError as e:
        current_app.logger.error(e)
        return render_template(
            'error.html',
            title='Your link has expired',
            link={
                'text': 'Send another link',
                'href': '/password/reset'
                }
        )
