from flask import Blueprint, request

from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler
from src.services.vul_service import get_vuls_project, get_vuls_api

base_api_url_vul = Blueprint('base_api_url_vul', __name__)

@base_api_url_vul.route('', methods=['GET'])
@bearer_token_required
def take_vuls():
    pid = request.args.get('pid')
    tid = request.args.get('tid')
    data = get_vuls_project(pid) if pid else get_vuls_api(tid)
    return ResponseHandler.success_without_message(data)
