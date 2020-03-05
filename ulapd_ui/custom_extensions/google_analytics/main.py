class GoogleAnalytics(object):
    """Add Google Analytics support to apps. Including form validation events"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        app.config.setdefault('GOOGLE_ANALYTICS_KEY', False)

        @app.context_processor
        def inject_global_values():
            return dict(
                google_analytics_key=app.config['GOOGLE_ANALYTICS_KEY']
            )

        # app.jinja_env.filters['build_form_errors'] = build_form_errors
