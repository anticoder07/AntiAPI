from flask import Blueprint, request

from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler
from src.services.topic_service import create_topic_service, take_topic_service, take_topics_service, \
    change_topic_name_service, delete_topic_service

base_api_url_topic = Blueprint('base_api_url_topic', __name__)


# GET /scan/v1/topics?pid=
# response: [{
#   topic_id:
# 	topic_name:
# 	update_at:
# 	create_at:
# }]
@base_api_url_topic.route('', methods=['GET'])
@bearer_token_required
def take_topics():
    pid = request.args.get('pid')
    id = request.args.get('id')

    data = take_topics_service(pid) if pid else take_topic_service(id)

    return ResponseHandler.success_without_message(data)


# POST /scan/v1/topics
# request: {
#   project_id:
#   topic_name:
# }
# response: {
#   topic_id
# 	topic_name:
# 	update_at:
# 	create_at:
# }
@base_api_url_topic.route('', methods=['POST'])
@bearer_token_required
def create_new_topic():
    data = request.get_json()
    topic = create_topic_service(data)
    return ResponseHandler.success_without_message(topic)


# PATCH /scan/v1/topics
# request: {
#   topic_id:
#   topic_name:
# }
# response: {
#   topic_id:
# 	topic_name:
# 	update_at:
# 	create_at:
# }
@base_api_url_topic.route('', methods=['PATCH'])
@bearer_token_required
def change_topic_name():
    data = request.get_json()
    topic = change_topic_name_service(data)
    return ResponseHandler.success_without_message(topic)


# DELETE /scan/v1/topics
# request: {
#     topic_id:
# }
# response: "Delete topic successfully"
@base_api_url_topic.route('', methods=['DELETE'])
@bearer_token_required
def delete_topic():
    data = request.get_json()
    msg = delete_topic_service(data)
    return ResponseHandler.success_without_message(msg)
