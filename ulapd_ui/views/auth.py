from flask import request, flash
from flask import g, current_app, render_template, redirect, make_response, Blueprint
from ulapd_ui.utils.validation import FormValidator, is_not_empty, email_validator
from ulapd_ui.utils.session import dps_session
from ulapd_ui.dependencies.api import api_get

AuthBlueprint = Blueprint('sign-in', __name__)


@AuthBlueprint.route('/sign-in', methods=['GET'])
def get_signin():
    # Redirect to homepage ig already signed in
    if g.user:
        return redirect(current_app.config.get("SITE_URL") + '/datasets')

    breadcrumb_links = [{"label": "Home", "href": "/"},
                        {"label": "Sign in to your account", "href": None}]

    resp = make_response(
        render_template("app/auth/signin.html", breadcrumb_links=breadcrumb_links)
    )

    # Set referrer cookie if coming to /sign-in from within site.
    # Used for redirecting user to previous page after successful sign in
    if request.referrer:
        if request.referrer.startswith(current_app.config.get("SITE_URL") + '/datasets'):
            resp.set_cookie('Referer', request.referrer)

    return resp


@AuthBlueprint.route('/sign-in', methods=['POST'])
def fail_signin():
    email = request.form['email']
    password = request.form['password']

    current_app.logger.info('Calling account-api to check lock status for {}'.format(email))
    api_url = '/api/account/users/{}/check_lock'.format(email)
    resp, code = api_get(api_url, headers={'Content-Type': 'application/json'})

    if 'locked' in resp and resp['locked'] is not None:
        current_app.logger.info('Users account is locked')
        breadcrumb_links = [{"label": "Home", "href": "/"},
                            {"label": "Sign in to your account", "href": None}]
        flash('Your account is locked. Check your email.')
        return render_template("app/auth/signin.html",
                               error_title="There was a problem",
                               breadcrumb_links=breadcrumb_links)

    form = FormValidator('Email or password not recognised')
    form.add_validator('email',
                       email,
                       [email_validator, is_not_empty])
    form.add_validator('password', password, is_not_empty)
    breadcrumb_links = [{"label": "Home", "href": "/"},
                        {"label": "Sign in to your account", "href": None}]

    return render_template("app/auth/signin.html",
                           error_title="There was a problem",
                           fields=form.validate(),
                           breadcrumb_links=breadcrumb_links)


@AuthBlueprint.route('/sign-out', methods=['GET', 'POST'])
def logout():
    resp = make_response(redirect('/'))

    # Expire 'signed in' cookies
    resp.set_cookie('AccessToken', '', expires=0)
    resp.set_cookie('Referer', '', expires=0)

    dps_session.destroy()
    return resp


@AuthBlueprint.route("/complete-sign-in", methods=['GET'])
def complete_sign_in():
    session = dps_session.get_state()

    # Redirect user to page before signing in if set
    referer = current_app.config.get('SITE_URL') + '/'
    if request.cookies.get('Referer') is not None:
        referer = request.cookies.get('Referer')

    return redirect(referer)
