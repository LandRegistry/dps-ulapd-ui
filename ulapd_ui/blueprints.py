# Import every blueprint file
from ulapd_ui.views import health
from ulapd_ui.views import datasets
from ulapd_ui.views import password
from ulapd_ui.views import general
from ulapd_ui.views import registration
from ulapd_ui.views import registration_personal
from ulapd_ui.views import registration_uk_organisation
from ulapd_ui.views import registration_overseas_org
from ulapd_ui.views import auth
from ulapd_ui.views import api


def register_blueprints(app):
    """
    Adds all blueprint objects into the app.
    """
    app.register_blueprint(health.health)
    app.register_blueprint(datasets.datasets)
    app.register_blueprint(password.password)
    app.register_blueprint(general.general)
    app.register_blueprint(registration.registration)
    app.register_blueprint(registration_personal.registration_personal)
    app.register_blueprint(registration_uk_organisation.registration_uk_organisation)
    app.register_blueprint(registration_overseas_org.registration_overseas_org)
    app.register_blueprint(auth.AuthBlueprint)
    app.register_blueprint(api.api, url_prefix='/api/v1')

    # All done!
    app.logger.info("Blueprints registered")
