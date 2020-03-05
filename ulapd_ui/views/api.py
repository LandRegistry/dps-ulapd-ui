from flask import Blueprint, current_app, jsonify, request
from ulapd_ui.exceptions import ApplicationError
from ulapd_ui.services import api_service
from ulapd_ui.utils.decorators import authorization_required, check_dataset_available

api = Blueprint('api', __name__)


@api.route('/datasets', methods=['GET'])
@authorization_required
def get_api_datasets():
    try:
        return jsonify(api_service.get_api_datasets())
    except ApplicationError as error:
        error_message = 'Failed to get datasets - {}'.format(error.message)
        current_app.logger.error(error_message)
        response = {
            "success": False,
            "error": error.message
        }
        return jsonify(response), error.http_code


@api.route('/datasets/<dataset>', methods=['GET'])
@authorization_required
@check_dataset_available
def get_api_dataset_name(dataset):
    try:
        return jsonify(api_service.get_api_dataset_by_name(dataset))
    except ApplicationError as error:
        error_message = 'Failed to get datasets - {}'.format(error.message)
        current_app.logger.error(error_message)
        response = {
            "success": False,
            "error": error.message
        }
        return jsonify(response), error.http_code


@api.route('/datasets/<dataset>/<file_name>', methods=['GET'])
@authorization_required
@check_dataset_available
def get_api_download_link(dataset, file_name):
    try:
        return jsonify(api_service.get_api_download_link(dataset, file_name))
    except ApplicationError as error:
        error_message = 'Failed to get datasets - {}'.format(error.message)
        current_app.logger.error(error_message)
        response = {
            "success": False,
            "error": error.message
        }
        return jsonify(response), error.http_code


@api.route('/datasets/history/<dataset>', methods=['GET'])
@authorization_required
@check_dataset_available
def get_api_dataset_history(dataset):
    try:
        return jsonify(api_service.get_api_dataset_history(dataset))
    except ApplicationError as error:
        error_message = 'Failed to get datasets - {}'.format(error.message)
        current_app.logger.error(error_message)
        response = {
            "success": False,
            "error": error.message
        }
        return jsonify(response)


@api.route('/datasets/history/<dataset>/<file_name>', methods=['GET'])
@authorization_required
@check_dataset_available
def get_api_history_download_link(dataset, file_name):
    try:
        date = file_name.strip(dataset.upper()).strip('_FULL_').strip('_COU_').rsplit('.')[0]
        return jsonify(api_service.get_api_download_link(dataset, file_name, date))
    except ApplicationError as error:
        error_message = 'Failed to get datasets - {}'.format(error.message)
        current_app.logger.error(error_message)
        response = {
            "success": False,
            "error": error.message
        }
        return jsonify(response), error.http_code
