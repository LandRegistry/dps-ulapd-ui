from flask import g, current_app, session
from ulapd_ui.utils.session import dps_session
from ulapd_ui.dependencies.ulapd_api import UlapdAPI


class SessionSetup(object):
    "Register handlers to setup dps_session"

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.setup_session(app)

    def setup_session(self, app):
        app.before_request(self.before_request)

    def before_request(self):
        g.user = None

        if dps_session.is_valid():
            sess = dps_session.populate_state(session)
            if 'user' in sess:
                email = sess['user']['principle']['email']
                g.user = email
                if not sess['user'].get('user_details'):
                    user_details = UlapdAPI().get_user_details('email', email)
                    sess['user'].update(user_details)
                    dps_session.commit()
            return

        if dps_session.is_set():
            current_app.logger.info('Session is already set')
        else:
            if dps_session.is_valid():
                dps_session.populate_state(session)
                current_app.logger.info('Session created')
            else:
                current_app.logger.info('Token expired')
