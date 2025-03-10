from flask import Blueprint

from src.commons.security.token_required import bearer_token_required

base_api_url_payload = Blueprint('base_api_url_payload', __name__)


# GET /scan/v1/payloads?id=
# response: {
#   "payload_id":
# 	"payload_content":
# 	"payload_type":
# 	"regex":
# 	"language":
# }
@base_api_url_payload.route('', methods=['GET'])
@bearer_token_required
def take_payload():
    return None


# GET /scan/v1/payloads?id=
# response: [{
#   "payload_id":
# 	"payload_content":
# 	"payload_type":
# 	"regex":
# 	"language":
# }]
@base_api_url_payload.route('', methods=['GET'])
@bearer_token_required
def take_payloads():
    return None


# POST /scan/v1/payloads
# request:{
# 	"payload_content":
# 	"payload_type":
# 	"regex":
# 	"language":
# }
# response: {
#   "payload_id":
# 	"payload_content":
# 	"payload_type":
# 	"regex":
# 	"language":
# }
@base_api_url_payload.route('', methods=['POST'])
@bearer_token_required
def create_new_payload():
    return None


# POST /scan/v1/payloads
# request:{
#   "payload_id":
# 	"payload_content":
# 	"payload_type":
# 	"regex":
# 	"language":
# }
# response: {
#   "payload_id":
# 	"payload_content":
# 	"payload_type":
# 	"regex":
# 	"language":
# }
@base_api_url_payload.route('', methods=['PATCH'])
@bearer_token_required
def change_payload():
    return None


# DELETE /scan/v1/payloads
# request: {
#   "payload_id":
# }
# response: "Delete payload successfully"
@base_api_url_payload.route('', methods=['DELETE'])
@bearer_token_required
def delete_payload():
    return None
