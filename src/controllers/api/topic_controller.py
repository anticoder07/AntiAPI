from datetime import datetime

from flask import Blueprint, request

from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler

base_api_url_topic = Blueprint('base_api_url_topic', __name__)


#
# # GET /api/v1/topics?id=
# # response: {
# # 	topic_name:
# # 	update_at:
# # 	create_at:
# # }
# @base_api_url_topic.route('', methods=['GET'])
# @bearer_token_required
# def take_topic():
#     return None
#
# # GET /api/v1/topics?pid=
# # response: [{
# # 	topic_name:
# # 	update_at:
# # 	create_at:
# # }]
# @base_api_url_topic.route('', methods=['GET'])
# @bearer_token_required
# def take_topics():
#     return None
#
# # POST /api/v1/topics
# # request: {
# #     topic_name:
# # }
# # response: {
# # 	topic_name:
# # 	update_at:
# # 	create_at:
# # }
# @base_api_url_topic.route('', methods=['POST'])
# @bearer_token_required
# def create_new_topic():
#     return None
#
# # PATCH /api/v1/topics
# # request: {
# #     topic_id:
# # }
# # response: {
# # 	topic_name:
# # 	update_at:
# # 	create_at:
# # }
# @base_api_url_topic.route('', methods=['PATCH'])
# @bearer_token_required
# def change_topic():
#     return None
#
# # DELETE /api/v1/topics
# # request: {
# #     topic_id:
# # }
# # response: "Delete topic successfully"
# @base_api_url_topic.route('', methods=['DELETE'])
# @bearer_token_required
# def delete_topic():
#     return None


@base_api_url_topic.route('', methods=['GET'])
@bearer_token_required
def take_topics():
    pid = request.args.get('pid')
    if pid:
        fake_data = [
            {
                'topic_id': 1,
                'topic_name': f'Topic {pid} - 1',
                'update_at': datetime.utcnow().isoformat(),
                'create_at': datetime.utcnow().isoformat()
            },
            {
                'topic_id': 2,
                'topic_name': f'Topic {pid} - 2',
                'update_at': datetime.utcnow().isoformat(),
                'create_at': datetime.utcnow().isoformat()
            }
        ]
    else:
        fake_data = [
            {
                'topic_id': 1,
                'topic_name': 'Topic 1',
                'update_at': datetime.utcnow().isoformat(),
                'create_at': datetime.utcnow().isoformat()
            },
            {
                'topic_id': 2,
                'topic_name': 'Topic 2',
                'update_at': datetime.utcnow().isoformat(),
                'create_at': datetime.utcnow().isoformat()
            },
            {
                'topic_id': 3,
                'topic_name': 'Topic 3',
                'update_at': datetime.utcnow().isoformat(),
                'create_at': datetime.utcnow().isoformat()
            }
        ]

    return ResponseHandler.success_without_message(fake_data)
