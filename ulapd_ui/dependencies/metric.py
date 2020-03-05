from flask import current_app
import requests
from ulapd_ui.app import app


def send_metric(dataset_id, activity, user_id, user_data, filename):
    try:
        current_app.logger.info('Start building the data for sending to dps_metric_api')

        metric_data = build_metric_data(dataset_id, activity, user_id, user_data, filename)

        metric_retry = app.config.get("METRIC_RETRY")

        for attempts in range(int(metric_retry)):
            current_app.logger.info('Attempt number {} trying to call dps_metric_api'.format((attempts+1)))
            try:
                # calling dps_metric_api outside api_post because download should not fail because of metric call
                response = metric_post(metric_data)
                current_app.logger.info('Call to dps_metric successful with response {}, and code {}'.format(
                                        response.text, response.status_code))
                if response.status_code > 399:
                    current_app.logger.error('Call to dps_metric_api failed on attempt {} with code {}'.format(
                                             attempts+1, response.status_code))
                else:
                    break
            except Exception as e:
                current_app.logger.error('Call to dps_metrics failed on attempt {} with error {}'.format(
                                         attempts+1, e))

        return metric_data
    except Exception as e:
        # no exception raised as sending to dps_metric_api should not stop download event
        current_app.logger.error('sending data to dps_metric_api failed with error: {}'.format(e))
        return 'Failed'


def build_metric_data(dataset_id, activity, user_id, user_data, filename):
    metric_data = {
        'user': {
            'ckan_user_id': str(user_id),
            'user_type': user_data['user_type']['user_type'],
            'status': 'Approved',
            'contactable': user_data['contactable']
        },
        'activity': {
            'activity_type': activity,
            'dataset': dataset_id,
            'filename': filename
        }
    }

    return metric_data


def metric_post(event_data):
    response = requests.Session().post(app.config.get("METRIC_API_URL"),
                                       json=event_data,
                                       headers={'Accept': 'application/json',
                                                'Content-Type': 'application/json'})
    return response
