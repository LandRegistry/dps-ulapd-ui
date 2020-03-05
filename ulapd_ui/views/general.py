import os
import markdown
from flask import Blueprint, render_template, redirect, request, current_app, g
from ulapd_ui.utils.decorators import requires_signed_in_user, refresh_user_session
from ulapd_ui.dependencies.ulapd_api import UlapdAPI
from ulapd_ui.utils.datasets_utilities import check_agreement
from ulapd_ui.utils.session import dps_session
from ulapd_ui.exceptions import ApplicationError
from os.path import dirname, abspath

general = Blueprint('general', __name__)
directory = os.path.dirname(__file__)


@general.route('/', methods=['GET'])
@refresh_user_session
def get_list():
    try:
        ulapd_api = UlapdAPI()
        session = dps_session.get_state()

        internal_datasets = ulapd_api.get_datasets()
        external_datasets = ulapd_api.get_external_datasets()

        # Filter out sample
        internal_datasets = [d for d in internal_datasets if '_sample' not in d['name']]

        # Add internal/external datasets together
        dataset_list = internal_datasets + external_datasets

        # Sort alphabetically putting datasets starting with numeric characters last
        dataset_list.sort(key=lambda d: 'z' if d['title'][0].isdigit() else d['title'])

        # User specific data
        user_access = {}
        api_key = ''
        user_has_activity = False
        if g.user:
            api_key = session['user']['user_details']['api_key']

            # Dictionary of datasets user has access to
            user_access = {d: True for d in session['user']['datasets']}

            # Check if user has downloaded anything for 'agreed licence but not downloaded' state
            user_activity = ulapd_api.get_user_download_activity(session['user']['user_details']['user_details_id'])
            user_has_activity = bool(user_activity)

        # Get dataset history for agreed datasets
        agreed_dataset_list = []
        for dataset in dataset_list:
            if check_agreement(dataset['name']):
                dataset['history'] = ulapd_api.get_dataset_history(dataset['name'])
                agreed_dataset_list.append(dataset)

        # Filter out confidential (e.g. DAD dataset) from listings page
        dataset_list = [d for d in dataset_list if 'confidential' != d['type']]
        freemium_licences = {}
        for dataset in user_access:
            if dataset == 'res_cov' or dataset == 'leases':
                dataset_licence = session['user']['datasets'][dataset]['licences']
                if len(dataset_licence) == 1:
                    licence_string = '{} licence'.format(dataset_licence[0])
                    freemium_licences[dataset] = licence_string
                else:
                    start = ", ".join(dataset_licence[:-1])
                    licence_string = '{} and {} licences'.format(start, dataset_licence[-1])
                    freemium_licences[dataset] = licence_string

        return render_template('app/datasets/index.html',
                               datasets_list=dataset_list,
                               api_key=api_key,
                               user_access=user_access,
                               agreed_dataset_list=agreed_dataset_list,
                               dps_session=session,
                               user_has_activity=user_has_activity,
                               freemium_licences=freemium_licences
                               )

    except ApplicationError as e:
        raise ApplicationError('Something went wrong when retrieving the datasets - error: {}'.format(e))


@general.route('/reset-api-key', methods=['POST'])
@requires_signed_in_user
def reset_api_key():
    try:
        session = dps_session.get_state()
        ulapd_api = UlapdAPI()

        user_id = session['user']['user_details']['user_details_id']
        ulapd_api.update_api_key(user_id)
        return redirect('/#my-api-key')
    except ApplicationError as e:
        raise ApplicationError('Something went wrong when resetting API key - error: {}'.format(e))


@general.route('/api-information', methods=['GET'])
def get_api_info():
    breadcrumb_links = [{"label": "Home", "href": "/"},
                        {"label": "Accessing data with our API", "href": None}]
    return render_template('app/general/api_info.html',
                           site_url=current_app.config.get("SITE_URL"),
                           breadcrumb_links=breadcrumb_links)


@general.route('/api-documentation', methods=['GET'])
def get_api_documentation():
    breadcrumb_links = [{"label": "Home", "href": "/"},
                        {"label": "API Documentation", "href": None}]

    return render_template('app/general/api_docs.html',
                           breadcrumb_links=breadcrumb_links,
                           site_url=current_app.config.get("SITE_URL"))


@general.route('/service-terms-of-use', methods=['GET'])
def get_terms_of_use():
    return render_template('app/general/service_terms.html')


@general.route('/accessibility-statement', methods=['GET'])
def get_accessibility_statement():
    return render_template('app/general/accessibility.html')


@general.route("/cookies", methods=['GET'], endpoint='cookies_info')
@general.route("/contact", methods=['GET'], endpoint='contact_info')
@general.route("/welsh", methods=['GET'], endpoint='welsh_info')
def get_link_info():
    directory = dirname(dirname(abspath(__file__)))
    md_file_path = '{0}/documents/{1}.md'.format(directory, request.url_rule)

    md_file_path = open(md_file_path, "r")
    md_content = md_file_path.read()
    md_renderer = markdown.Markdown()
    md_html = md_renderer.convert(md_content)

    if request.url_rule == "contact":
        return render_template('app/links/{0}.html'.format(request.url_rule))
    else:
        return render_template('app/links/{0}.html'.format(request.url_rule), md=md_html)


@general.route("/session-expired", methods=['GET'])
def get_session_expired():
    return render_template('app/session-expired.html')
