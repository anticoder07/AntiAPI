from flask import Blueprint, request

from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler
from src.services.api.api_service import create_new_api_service, delete_api_service, get_apis_service, get_api_service

base_api_url_api = Blueprint('base_api_url_api', __name__)


# GET /api/v1/apis?pid=
# response: [{
# 	topic_id:
# 	api_name:
# 	api_type:
# 	format_api:
# 	endpoint:
# }]
@base_api_url_api.route('', methods=['GET'])
@bearer_token_required
def take_apis():
    tid = request.args.get('tid')
    id = request.args.get('id')

    apis = get_apis_service(tid) if tid else get_api_service(id)

    return ResponseHandler.success_without_message(apis)


# POST /api/v1/apis
# request: {
#   topic_id:
# 	api_name:
# 	api_type:
# 	format_api:
# 	endpoint:
# }
# response: {
# 	topic_id:
# 	api_name:
# 	api_type:
# 	format_api:
# 	endpoint:
# }
@base_api_url_api.route('', methods=['POST'])
@bearer_token_required
def create_new_api():
    data = request.json
    api = create_new_api_service(data)
    return ResponseHandler.success_without_message(api)


# DELETE /api/v1/apis
# request: {
# 	api_id:
# }
# response: "Delete api successfully"
@base_api_url_api.route('', methods=['DELETE'])
@bearer_token_required
def delete_api():
    data = request.json
    msg = delete_api_service(data)
    return ResponseHandler.success(msg)
