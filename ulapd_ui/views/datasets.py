import os
import markdown

from flask import g, Blueprint, render_template, redirect, request, url_for, current_app
from ulapd_ui.utils.session import dps_session
from ulapd_ui.exceptions import ApplicationError
from ulapd_ui.utils.decorators import requires_signed_in_user, refresh_user_session
from ulapd_ui.dependencies.ulapd_api import UlapdAPI
from ulapd_ui.dependencies.metric import send_metric
from ulapd_ui.utils.datasets_utilities import accept_licence, check_agreement, \
    historic_date_formatter, build_dataset_details, build_rfi_dataset_for_download

directory = os.path.dirname(__file__)

datasets = Blueprint(
    'datasets',
    __name__,
    url_prefix="/datasets")


@datasets.route("", methods=['GET'])
def redirect_to_home_page():
    return redirect('/')


@datasets.route("/<dataset_id>", methods=['GET'])
@refresh_user_session
def get_details(dataset_id):
    try:
        ulapd_api = UlapdAPI()
        session = dps_session.get_state()

        if dataset_id == 'nps_sample':
            return redirect(url_for('.get_details', dataset_id='nps'))

        # Go get the individual dataset details
        dataset_details = ulapd_api.get_dataset_by_name(dataset_id)

        # Fail nicely if the dataset doesnt exist
        if dataset_id not in dataset_details['name']:
            raise ApplicationError('Unable to display dataset details: dataset does not exist', http_code=404)

        # Now get the example json and to our dataset list
        extras = build_dataset_details(dataset_id)

        # Add details to dataset
        dataset_details.update(extras)

        # get dataset for dataset_id to check private boolean, if false is non restricted, if true is restricted
        is_restricted = dataset_details['private']

        licence_signed = check_agreement(dataset_id)

        if dataset_id == 'nps':
            licence_signed = {
                'nps': check_agreement(dataset_id),
                'nps_sample': check_agreement('nps_sample')
            }

        # Handle freemium licencing:
        # If a user has signed exploratory/commercial licences they should still be able to sign direct licence
        if dataset_details['type'] == 'freemium':
            if g.user:
                licence_signed = True
                dataset = session['user']['datasets'].get(dataset_id)

                if not dataset:
                    licence_signed = False

                if dataset:
                    if 'Direct Use' not in dataset['licences']:
                        licence_signed = False

                    if len(dataset['licences']) == 1:
                        if 'Direct' in dataset['licences'][0] and not dataset['valid_licence']:
                            licence_signed = False

        current_app.logger.info('Displaying details for user requested dataset: {}'.format(dataset_id))

        breadcrumb_links = [{"label": "Home", "href": "/"},
                            {"label": dataset_details['title'], "href": None}]

        return render_template("app/datasets/{}/details.html".format(dataset_id),
                               dataset_details=dataset_details,
                               licence_signed=licence_signed,
                               is_restricted=is_restricted,
                               readable_date=dataset_details['last_updated'], breadcrumb_links=breadcrumb_links)
    except ApplicationError as e:
        raise ApplicationError('Something went wrong when retrieving dataset details: {}'.format(e))


@datasets.route("/<dataset_id>/licence/view", methods=['GET'])
@datasets.route("/<dataset_id>/licence/<licence_type>/view", methods=['GET'])
@refresh_user_session
def view_licence(dataset_id, licence_type=None):
    try:
        if licence_type:
            current_app.logger.info('Displaying view {} licence page for dataset: {}'.format(licence_type, dataset_id))
            return render_template("app/datasets/licence.html", licence_type=licence_type, dataset_id=dataset_id)
        else:
            licence_file = open(os.path.join(directory, '../documents/datasets/{}/licence.md').format(dataset_id), "r")
            md_licence = licence_file.read()
            md_renderer = markdown.Markdown()
            md_html = md_renderer.convert(md_licence)

            current_app.logger.info('Displaying view licence page for dataset: {}'.format(dataset_id))
            return render_template("app/datasets/licence.html", dataset_id=dataset_id, md=md_html)
    except Exception as e:
        raise ApplicationError('Something went wrong when retrieving licence view page: {}'.format(e))


@datasets.route("/<dataset_id>/tech-spec", methods=['GET'])
@datasets.route("/<dataset_id>/tech-spec/<tech_spec_no>", methods=['GET'])
def get_tech_spec(dataset_id, tech_spec_no=None):
    if tech_spec_no:
        return render_template('app/datasets/{}/tech_spec_{}.html'.format(dataset_id, tech_spec_no),
                               dataset_id=dataset_id)
    else:
        return render_template('app/datasets/{}/tech_spec.html'.format(dataset_id), dataset_id=dataset_id)


@datasets.route("/<dataset_id>/licence/agree", methods=['GET'])
@requires_signed_in_user
@refresh_user_session
def get_agree_licence(dataset_id):
    try:
        ulapd_api = UlapdAPI()
        dataset_details = ulapd_api.get_dataset_by_name(dataset_id)
        accepted = check_agreement(dataset_id)

        if dataset_details['type'] == 'freemium':
            accepted = True
            session = dps_session.get_state()
            dataset = session['user']['datasets'].get(dataset_id)

            if not dataset:
                accepted = False

            if dataset:
                if 'Direct Use' not in dataset['licences']:
                    accepted = False

                if len(dataset['licences']) == 1:
                    if 'Direct' in dataset['licences'][0] and not dataset['valid_licence']:
                        accepted = False

            if not accepted:
                return render_template(
                    "app/datasets/licence.html",
                    agree=True,
                    dataset_id=dataset_id,
                    licence_type='direct'
                )

        if accepted:
            current_app.logger.info('Redirecting to download page for dataset: {}'.format(dataset_id))
            return redirect(url_for('.get_details', dataset_id=dataset_id))

        licence_file = open(os.path.join(directory, '../documents/datasets/{}/licence.md').format(dataset_id), "r")
        md_licence = licence_file.read()
        md_renderer = markdown.Markdown()
        md_html = md_renderer.convert(md_licence)
        current_app.logger.info('Displaying agree licence page for dataset: {}'.format(dataset_id))

        return render_template("app/datasets/licence.html", agree=True, dataset_id=dataset_id, md=md_html)
    except Exception as e:
        raise ApplicationError('Something went wrong when retrieving licence agree page: {}'.format(e))


@datasets.route("/<dataset_id>/licence/agree", methods=['POST'])
@requires_signed_in_user
def post_agree_licence(dataset_id):
    try:
        ulapd_api = UlapdAPI()
        dataset_details = ulapd_api.get_dataset_by_name(dataset_id)

        if request.form.get('agree-licence') is None:
            is_freemium = dataset_details['type'] == 'freemium'

            md_html = ''

            # Until we convert licence MD files to HTML
            if not is_freemium:
                licence_file = open(os.path.join(directory, f'../documents/datasets/{dataset_id}/licence.md'), "r")
                md_licence = licence_file.read()
                md_renderer = markdown.Markdown()
                md_html = md_renderer.convert(md_licence)

            current_app.logger.info('Displaying licence page with errors for dataset: {}'.format(dataset_id))
            error_msg = 'You need to agree to the terms and conditions to download data'
            return render_template("app/datasets/licence.html",
                                   agree=True,
                                   dataset_id=dataset_id,
                                   licence_type='direct',
                                   md=md_html,
                                   error_title="There are errors on this page",
                                   fields={'agree-licence': {'data': '', 'error': [error_msg]}})
        else:
            # Prevent users signing licences for nps/dad etc via the service
            if dataset_details['type'] not in ['confidential', 'restricted']:
                accept_licence(dataset_id)
                current_app.logger.info('Redirecting to download page for dataset: {}'.format(dataset_id))
                session = dps_session.get_state()

                if dataset_id == 'nps_sample':
                    return redirect(url_for('.get_details', dataset_id='nps'))

            return redirect(url_for('general.get_list'))
    except Exception as e:
        raise ApplicationError('Something went wrong when retrieving licence agree page: {}'.format(e))


@datasets.route("/<dataset_id>/download", methods=['GET'])
@refresh_user_session
def get_download_page(dataset_id):
    ulapd_api = UlapdAPI()

    if dataset_id == 'rfi':
        dataset, history = build_rfi_dataset_for_download(ulapd_api.get_dataset_by_name(dataset_id),
                                                          ulapd_api.get_dataset_history(dataset_id))
    else:
        dataset = ulapd_api.get_dataset_by_name(dataset_id)
        history = ulapd_api.get_dataset_history(dataset_id)

    breadcrumb_links = [{"label": "Home", "href": "/"},
                        {"label": dataset['title'], "href": "/datasets/"+dataset['name']},
                        {"label": "Download dataset", "href": None}]

    return render_template('app/datasets/{}/download.html'.format(dataset_id), dataset=dataset, history=history,
                           breadcrumb_links=breadcrumb_links)


@datasets.route("/<dataset_id>/download/<file_name>", methods=['GET'], defaults={'last_updated': None})
@datasets.route("/<dataset_id>/download/history/<last_updated>/<file_name>", methods=['GET'])
@refresh_user_session
def download(dataset_id, file_name, last_updated):
    try:
        ulapd_api = UlapdAPI()

        dataset = ulapd_api.get_dataset_by_name(dataset_id)

        # First check to see if its a public resource
        if last_updated is None:
            for resource in dataset['public_resources']:
                current_app.logger.info("Public: " + str(resource['file_name']))
                if resource['file_name'] == file_name:
                    current_app.logger.info("Public file download, skipping checks")
                    url = ulapd_api.get_download_link(dataset_id, resource['file_name'])
                    return redirect(url['link'])

        if dataset['type'] != 'open':
            # Need the session to get infor about the dataset and user
            session = dps_session.get_state()
            user_id = session['user']['user_details']['user_details_id']
            user_data = session['user']['user_details']

            # 1. Check if user is authenticated
            if not dps_session.is_logged_in():
                return '/sign-in'

            # 2. Check if user has signed the correct licence
            if check_agreement(dataset_id) is not True:
                current_app.logger.info("User has no access to dataset")
                return url_for('datasets.get_agree_licence', dataset_id=dataset_id)

            # 3. Generate link
            if last_updated:
                last_updated = historic_date_formatter(last_updated, dataset['update_frequency'])
                url = ulapd_api.get_history_download_link(dataset_id, file_name, last_updated)
                activity = 'history download'
            else:
                url = ulapd_api.get_download_link(dataset_id, file_name)
                activity = 'download'

            # 4. Track the download and return (create activity)
            ulapd_api.create_activity(session['user']['user_details']['user_details_id'],
                                      "download", request.remote_addr, False, file_name, dataset_id)

            send_metric(dataset_id, activity + " ui", user_id, user_data, file_name)
        else:
            # 1. Generate link
            if last_updated:
                last_updated = historic_date_formatter(last_updated, dataset['update_frequency'])
                url = ulapd_api.get_history_download_link(dataset_id, file_name, last_updated)
            else:
                url = ulapd_api.get_download_link(dataset_id, file_name)

        return redirect(url['link'])
    except Exception as e:
        raise ApplicationError('Tracking download has failed - error: {}'.format(e))
