from flask import session, request, current_app
from ulapd_ui.dependencies.api import api_get, api_put


class dps_session:
    @classmethod
    def is_valid(self):
        if 'AccessToken' in request.cookies:
            current_app.logger.info('AccessToken is ' + request.cookies['AccessToken'])
            token = request.cookies['AccessToken']
            _, status = api_get('/api/session/{}'.format(token))
            if status == 204:
                return True
        self.destroy()
        return False

    @classmethod
    def populate_state(self, session):
        if 'AccessToken' in request.cookies:
            current_app.logger.info('AccessToken is ' + request.cookies['AccessToken'])
            token = request.cookies['AccessToken']
            content, status = api_get('/api/session/{}/state'.format(token))
            if status == 200:
                session['dps-session'] = content
                return session['dps-session']
        self.destroy()
        return {}

    @classmethod
    def get_state(self):
        if 'dps-session' in session:
            return session['dps-session']
        return {}

    @classmethod
    def is_set(self):
        if not self.is_valid():
            return False
        return 'dps-session' in session

    @classmethod
    def is_logged_in(self):
        if self.is_set():
            return 'user' in session['dps-session']
        return False

    @classmethod
    def destroy(self):
        if 'dps-session' in session:
            del session['dps-session']

    # How to use this method:
    # session = dps_session.get_state()
    # session['test'] = {'added': 'true'}
    # dps_session.commit()
    @classmethod
    def commit(self):
        if self.is_valid():
            token = request.cookies['AccessToken']
            headers = {
                'Content-Type': 'application/json',
            }
            current_app.logger.info('Updating new session state for:' + token)
            _, status = api_put('/api/session/{}/state'.format(token),
                                json=session['dps-session'],
                                headers=headers)
            if status > 299:
                current_app.logger.error('A problem happened with committing the session')
