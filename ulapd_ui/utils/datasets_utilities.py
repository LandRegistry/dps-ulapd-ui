import os
import json
import time
from datetime import datetime

from flask import g, current_app
from ulapd_ui.utils.session import dps_session
from ulapd_ui.exceptions import ApplicationError
from ulapd_ui.dependencies.metric import send_metric
from ulapd_ui.dependencies.ulapd_api import UlapdAPI
from ulapd_ui.app import app

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def accept_licence(dataset_id):
    session = dps_session.get_state()
    try:
        ulapd_api = UlapdAPI()
        user_details = session['user']['user_details']

        send_metric(dataset_id, 'licence agreed', user_details['user_details_id'], user_details, None)

        data = {
            'user_details_id': user_details['user_details_id'],
            'licence_id': dataset_id
        }

        ulapd_api.create_licence_agreement(data)

    except Exception as e:
        raise ApplicationError('Error accepting licence: {}'.format(str(e)))


def check_agreement(dataset_id):
    if g.user:
        session = dps_session.get_state()
        dataset = session['user']['datasets'].get(dataset_id)
        if dataset:
            return dataset['valid_licence']

    return False


def historic_date_formatter(string, update_frequency):
    if update_frequency == 'Daily':
        date_timestamp = datetime.strptime(string, '%d %B %Y').timetuple()
        last_update = time.strftime('%Y_%m_%d', date_timestamp)
    else:
        date_timestamp = datetime.strptime(string, '%B %Y').timetuple()
        last_update = time.strftime('%Y_%m', date_timestamp)

    return last_update


def get_latest_download_activities(download_activities):
    latest_download_activities = []
    dataset_ids = set([d['dataset_id'] for d in download_activities])

    for dataset_id in dataset_ids:
        dataset_activities = [d for d in download_activities if d['dataset_id'] == dataset_id]
        latest = max(dataset_activities, key=lambda x: datetime.strptime(x['timestamp'], '%a, %d %b %Y %H:%M:%S %Z'))
        latest_download_activities.append(latest)

    return latest_download_activities


def build_download_history():
    download_history = []
    session = dps_session.get_state()

    if g.user:
        try:
            ulapd_api = UlapdAPI()
            user_id = session['user']['user_details']['user_details_id']
            download_activities = ulapd_api.get_user_download_activity(user_id)
            download_activities = get_latest_download_activities(download_activities)

            if download_activities:
                for download_activity in download_activities:
                    dataset_id = download_activity['dataset_id']
                    package_details = ulapd_api.get_dataset_by_name(dataset_id)

                    download_datetime = datetime.strptime(download_activity['timestamp'], '%a, %d %b %Y %H:%M:%S %Z')
                    last_update_datetime = datetime.strptime(package_details['last_updated'], '%d %B %Y')
                    is_latest_download = False if download_datetime < last_update_datetime else True

                    licence_agree_string = None
                    license_exists = package_details.get('licence_id')
                    if license_exists:
                        licence_agree_date = session['user']['datasets'][dataset_id]['date_agreed']
                        licence_agree_datetime = datetime.strptime(licence_agree_date, '%a, %d %b %Y %H:%M:%S %Z')
                        licence_agree_string = datetime.strftime(licence_agree_datetime, '%d %B %Y')

                    download_history.append({
                        'dataset_id': dataset_id,
                        'dataset_title': package_details['title'],
                        'last_download_date': datetime.strftime(download_datetime, '%d %B %Y'),
                        'last_update_date': datetime.strftime(last_update_datetime, '%d %B %Y'),
                        'licence_exists': license_exists,
                        'is_latest_download': is_latest_download,
                        'licence_agree_date': licence_agree_string,
                        'is_licence_agreed': check_agreement(dataset_id),
                        'resources': package_details['resources']
                        })

        except Exception as e:
            raise ApplicationError('Error building download history: {}'.format(e))

    current_app.logger.info('Returning history of file downloads: {}'.format(download_history))
    return download_history


def build_dataset_details(dataset_id, full_info=True):
    try:
        dataset = {}

        if full_info is False:
            return dataset

        # If full info is set to True the method will continue to fetch more information from documents directory
        dataset_sample = json.loads(open(directory + "/documents/datasets/{}/sample.json".format(
                                    dataset_id), 'r').read())

        details = {
            "example_data": dataset_sample.get('example_data', {})
        }

        # Add details to dataset
        dataset.update(details)

        return dataset
    except Exception as e:
        raise ApplicationError('Error building dataset details: {}'.format(e))


def build_rfi_dataset_for_download(dataset, history):
    app.logger.info('Building RFI dataset details for downloading...')
    file = dataset['resources'][0]['file_name']
    format_index = file.index('.csv')
    month_range = quarter_switcher(file[format_index - 2: format_index])
    dataset['month_range'] = month_range

    view_base_url = 'https://www.gov.uk/government/uploads/system/uploads/attachment_data/file'
    dataset['view_url'] = '{}{}'.format(view_base_url, '/855791/RI_Top_500_Customers_2019_Q3.csv/preview')

    view_url_history = [
        '/840544/RI_Top_500_Customers_2019_Q2.csv/preview',
        '/813817/RI_Top_500_Customers_2019_Q1.csv/preview',
        '/794788/request_information_top_500_customers_2019_q4.csv/preview',
        '/793232/RI_Top_500_Customers_2018_Q3.csv/preview',
        '/793246/RI_Top_500_Customers_2018_Q2.csv/preview',
        '/788563/RI_Top_500_Customers_2018_Q1.csv/preview'
    ]

    years_list = []
    dataset_list = []
    for index, rows in enumerate(history['dataset_history']):

        file = rows['resource_list'][0]['file_name']
        format_index = file.index('.csv')
        quarter = file[format_index - 2: format_index]
        month_range = quarter_switcher(quarter)

        year = int(rows['last_updated'][-4:])
        if quarter == 'Q3':
            year -= 1

        this_dataset = rows
        this_dataset['year'] = year
        this_dataset['month_range'] = month_range
        this_dataset['view_url_history'] = '{}{}'.format(view_base_url, view_url_history[index])

        history['dataset_history'][index]['year'] = year
        dataset_list.append(this_dataset)

        if year not in years_list:
            years_list.append(year)

    history_list = []
    for rows in years_list:
        details = [d for d in dataset_list if rows == d['year']]
        history_dict = {
            'year': rows,
            'details': details
        }
        history_list.append(history_dict)

    app.logger.info('Returning RFI dataset details for downloading...')
    return dataset, history_list


def quarter_switcher(quarter):
    month_range = {
        'Q1': 'April to June',
        'Q2': 'July to September',
        'Q3': 'October to December',
        'Q4': 'January to March'
    }

    return month_range.get(quarter, None)
