from flask import request, Blueprint
from datetime import datetime
from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler

base_api_url_api = Blueprint('base_api_url_api', __name__)

@base_api_url_api.route('', methods=['GET'])
@bearer_token_required
def take_apis():
    pid = request.args.get('tid')

    fake_data = [
        {
            "topic_id": pid if pid else "default_topic",
            "api_name": f"API {pid} - 1" if pid else "API 1",
            "api_type": "REST",
            "format_api": "JSON",
            "endpoint": f"/api/v1/apis/{pid}/data" if pid else "/api/v1/apis/1/data"
        },
        {
            "topic_id": pid if pid else "default_topic",
            "api_name": f"API {pid} - 2" if pid else "API 2",
            "api_type": "GraphQL",
            "format_api": "GraphQL",
            "endpoint": f"/api/v1/apis/{pid}/query" if pid else "/api/v1/apis/2/query"
        }
    ]

    return ResponseHandler.success_without_message(fake_data)
