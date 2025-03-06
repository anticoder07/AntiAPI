from flask import Blueprint

from src.commons.security.token_required import bearer_token_required

base_api_url_vul = Blueprint('base_api_url_vul', __name__)


# GET /api/v1/vul?id=
# response: {
# 	api_id:
# 	payload:
# 	vul_type:
# 	vul_status:
# 	regex_fix:
# }
@base_api_url_vul.route('', methods=['GET'])
@bearer_token_required
def take_vul():
    return None


# GET /api/v1/vul?pid=
# response: [{
# 	api_id:
# 	payload:
# 	vul_type:
# 	vul_status:
# 	regex_fix:
# }]
@base_api_url_vul.route('', methods=['GET'])
@bearer_token_required
def take_vuls():
    return None
