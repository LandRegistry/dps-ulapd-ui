from functools import wraps
from common_utilities import errors
from flask import redirect, g, request, jsonify, current_app
from ulapd_ui.exceptions import ApplicationError
from ulapd_ui.utils.session import dps_session
from ulapd_ui.dependencies.ulapd_api import UlapdAPI


def refresh_user_session(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            if g.user:
                ulapd_api = UlapdAPI()
                session = dps_session.get_state()

                user_details = ulapd_api.get_user_details('email', g.user)
                session['user'].update(user_details)
                dps_session.commit()

            return f(*args, **kwargs)
        except Exception as e:
            raise ApplicationError('Something went wrong when refreshing user session: {}'.format(e))
    return decorated


def requires_signed_in_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user:
            return f(*args, **kwargs)
        else:
            current_app.logger.info('User not signed in')
            return redirect('/sign-in')
    return decorated


def handle_errors(is_get):
    def wrapper(func):
        def run_and_handle(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ApplicationError as error:
                raise error
        return run_and_handle
    return wrapper


# --- API decorators --- #
def authorization_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            if request.headers.get('Authorization') is None:
                raise ApplicationError('Access denied: You need to provide your API Key to perform this operation',
                                       http_code=403)
            return func(*args, **kwargs)
        except ApplicationError as error:
            response = {
                "success": False,
                "error": error.message
            }
            return jsonify(response), error.http_code
    return decorated


def check_dataset_available(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            ulapd_api = UlapdAPI()
            api_key = request.headers.get('Authorization')
            name = kwargs['dataset']
            dataset = ulapd_api.get_dataset_by_name(name)

            # Prevent 'open' datasets being accessed via API
            if dataset['type'] == 'open':
                raise ApplicationError(*errors.get('ulapd_ui', 'DATASET_NOT_FOUND', filler=name), http_code=404)

            # Prevent 'confidential' datasets being available via API if user doesn't have access
            if dataset['type'] == 'confidential':
                try:
                    user_access = ulapd_api.get_user_details('api_key', api_key)['datasets']
                except ApplicationError:
                    raise ApplicationError(*errors.get('ulapd_ui', 'API_KEY_ERROR', filler=api_key), http_code=404)

                if not user_access.get(name, False):
                    raise ApplicationError(*errors.get('ulapd_ui', 'DATASET_NOT_FOUND', filler=name), http_code=404)

            return f(*args, **kwargs)
        except ApplicationError as e:
            return jsonify({'success': False, 'error': e.message}), e.http_code

    return decorated
