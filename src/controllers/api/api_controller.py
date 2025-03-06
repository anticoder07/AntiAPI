from flask import Blueprint

from src.commons.security.token_required import bearer_token_required

base_api_url_api = Blueprint('base_api_url_api', __name__)


## Lưu ý: Nhớ check xem với người dùng có phải là người được phép truy cập api hay không

# GET /api/v1/apis?id=
# response: {
# 	topic_id:
# 	api_name:
# 	api_type:
# 	format_api:
# 	endpoint:
# }
@base_api_url_api.route('', methods=['GET'])
@bearer_token_required
def take_api():
    return None

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
    return None

# POST /api/v1/apis
# request: {
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
    return None

# DELETE /api/v1/apis
# request: {
# 	api_id:
# }
# response: "Delete api successfully"
@base_api_url_api.route('', methods=['DELETE'])
@bearer_token_required
def delete_api():
    return None