from flask import current_app, request
from ulapd_ui.dependencies.ulapd_api import UlapdAPI
from ulapd_ui.dependencies.metric import send_metric
from ulapd_ui.exceptions import ApplicationError
from ulapd_ui.utils.decorators import handle_errors
from common_utilities import errors


@handle_errors(is_get=True)
def get_api_datasets(external=False):
    ulapd_api = UlapdAPI()

    dataset_list = ulapd_api.get_datasets()
    user_details = _authenticate(ulapd_api)
    user_access = user_details['datasets']

    if dataset_list:
        # Filter out 'open' datasets
        dataset_list = [d for d in dataset_list if d['type'] != 'open']

        result_data = []
        for dataset in dataset_list:
            # Don't show 'confidential' datasets unless user has access
            if dataset['type'] == 'confidential':
                if user_access.get(dataset['name']):
                    result_data.append(dict(name=dataset['name'], title=dataset['title']))
            else:
                result_data.append(dict(name=dataset['name'], title=dataset['title']))

        response = {
            "success": True,
            "result": result_data
        }
        return response
    else:
        raise ApplicationError(*errors.get('ulapd_ui', 'NO_DATASETS_FOUND'), http_code=404)


@handle_errors(is_get=True)
def get_api_dataset_by_name(name):
    ulapd_api = UlapdAPI()

    # authenticate
    _authenticate(ulapd_api)

    dataset_details = ulapd_api.get_dataset_by_name(name)

    if dataset_details:
        response = {
            "success": True,
            "result": dataset_details
        }
        return response
    else:
        raise ApplicationError(*errors.get('ulapd_ui', 'DATASET_NOT_FOUND', filler=name), http_code=404)


@handle_errors(is_get=True)
def get_api_download_link(dataset_name, file_name, date=None):
    try:
        ulapd_api = UlapdAPI()
        dataset_details = ulapd_api.get_dataset_by_name(dataset_name)

        # authenticate
        user_details = _authenticate(ulapd_api)

        # check agreement
        agreement = user_details['datasets'].get(dataset_name)
        if not agreement:
            if dataset_details['private'] is True:
                raise ApplicationError(
                        *errors.get('ulapd_ui', 'NO_DATASET_ACCESS', filler=dataset_name),
                        http_code=403
                      )

            raise ApplicationError(*errors.get('ulapd_ui', 'NO_LICENCE_SIGNED', filler=dataset_name), http_code=403)
        if agreement['valid_licence'] is False:
            raise ApplicationError(*errors.get('ulapd_ui', 'NO_LICENCE_SIGNED', filler=dataset_name), http_code=403)

        # check to see if the filename exists for history files
        if date:
            resource_exists = False
            history_details = ulapd_api.get_dataset_history(dataset_name)
            for history in history_details['dataset_history']:
                exist = any(map(lambda resource: resource['file_name'] == file_name, history['resource_list']))
                if exist:
                    resource_exists = True
                    break
        else:
            # check to see if the filename exists for latest files
            resource_exists = any(map(lambda resource: resource['file_name'] == file_name,
                                      dataset_details['resources']))
        if not resource_exists:
            # check to see if the filename exists for public files
            if 'public_resources' in dataset_details:
                public_exists = any(map(lambda public: public['file_name'] == file_name,
                                        dataset_details['public_resources']))
                if not public_exists:
                    raise ApplicationError(*errors.get('ulapd_ui', 'FILE_DOES_NOT_EXIST', filler=file_name),
                                           http_code=404)
            else:
                raise ApplicationError(*errors.get('ulapd_ui', 'FILE_DOES_NOT_EXIST', filler=file_name), http_code=404)

        if date:
            link = ulapd_api.get_history_download_link(dataset_name, file_name, date)
        else:
            link = ulapd_api.get_download_link(dataset_name, file_name)
        if link:
            response = {
                "success": True,
                "result": {
                    "resource": file_name,
                    "valid_for_seconds": 10,
                    "download_url": link["link"]
                }
            }

            # Activity create
            ulapd_api.create_activity(user_details['user_details']['user_details_id'], 'download',
                                      request.remote_addr, True, file_name, dataset_name)

            send_metric(dataset_name, 'download api', user_details['user_details']['user_details_id'],
                        user_details['user_details'], file_name)
            return response
        else:
            current_app.logger.error('There was a problem getting the resource: '.format(file_name))
            raise ApplicationError(*errors.get('ulapd_ui', 'DATASET_NOT_FOUND', filler=dataset_name), http_code=404)
    except ApplicationError as error:
        raise error
    except Exception as e:
        raise e


def get_api_dataset_history(name):
    ulapd_api = UlapdAPI()

    # authenticate
    _authenticate(ulapd_api)

    history_details = ulapd_api.get_dataset_history(name)
    if history_details:
        history_data = []
        for history in history_details['dataset_history']:
            for file in history['resource_list']:
                history_info = {
                    "last_updated": history["last_updated"],
                    "unsorted_date": history["unsorted_date"],
                    "filename": file['file_name'],
                    "file_size": file['file_size']
                }
                history_data.append(history_info)

        response = {
            "success": True,
            "dataset": name,
            "dataset_history": history_data
        }

        return response
    else:
        current_app.logger.error('Dataset {} not found'.format(name))
        raise ApplicationError(*errors.get('ulapd_ui', 'DATASET_NOT_FOUND', filler=name), http_code=404)


def _authenticate(ulapd_api):
    api_key = request.headers.get('Authorization')
    try:
        user_details = ulapd_api.get_user_details('api_key', api_key)
    except ApplicationError:
        raise ApplicationError(*errors.get('ulapd_ui', 'API_KEY_ERROR', filler=api_key), http_code=404)
    return user_details
