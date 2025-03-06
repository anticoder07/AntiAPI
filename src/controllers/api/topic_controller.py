from flask import Blueprint

from src.commons.security.token_required import bearer_token_required

base_api_url_topic = Blueprint('base_api_url_topic', __name__)

# GET /api/v1/topics?id=
# response: {
# 	topic_name:
# 	update_at:
# 	create_at:
# }
@base_api_url_topic.route('', methods=['GET'])
@bearer_token_required
def take_topic():
    return None

# GET /api/v1/topics?pid=
# response: [{
# 	topic_name:
# 	update_at:
# 	create_at:
# }]
@base_api_url_topic.route('', methods=['GET'])
@bearer_token_required
def take_topics():
    return None

# POST /api/v1/topics
# request: {
#     topic_name:
# }
# response: {
# 	topic_name:
# 	update_at:
# 	create_at:
# }
@base_api_url_topic.route('', methods=['POST'])
@bearer_token_required
def create_new_topic():
    return None

# PATCH /api/v1/topics
# request: {
#     topic_id:
# }
# response: {
# 	topic_name:
# 	update_at:
# 	create_at:
# }
@base_api_url_topic.route('', methods=['PATCH'])
@bearer_token_required
def change_topic():
    return None

# DELETE /api/v1/topics
# request: {
#     topic_id:
# }
# response: "Delete topic successfully"
@base_api_url_topic.route('', methods=['DELETE'])
@bearer_token_required
def delete_topic():
    return None
