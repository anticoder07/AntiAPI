from flask import Blueprint, request

from src.payloads.responses.response_handler import ResponseHandler
from src.services.middle_service import handler_request, disable_middleware

base_api_url_middle = Blueprint('base_api_url_middle', __name__)


@base_api_url_middle.route('/<api_id>/<path:endpoint>', methods=['POST'])
def filtering(api_id, endpoint):
    full_request = {
        "method": request.method,
        "headers": dict(request.headers),
        "query_params": request.args.to_dict(),
        "body": request.get_json() if request.is_json else request.form.to_dict(),
        "files": request.files.to_dict(),
        "full_url": request.url
    }

    data = request.json

    query_string = request.query_string.decode('utf-8')

    if query_string:
        endpoint_full = f"{endpoint}?{query_string}"
    else:
        endpoint_full = endpoint

    msg = handler_request(api_id, endpoint_full, data, request.method, full_request)
    return msg


@base_api_url_middle.route('/enable', methods=['POST'])
def enable_middleware():
    data = request.json

    return ResponseHandler.success(enable_middleware(data))


@base_api_url_middle.route('/disable', methods=['POST'])
def disable_middleware():
    data = request.json

    return ResponseHandler.success(disable_middleware(data))
