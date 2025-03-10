from http.client import responses

from flask import Blueprint, request

from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler
from src.services.scan.scan_second_service import scan_api_2
from src.services.scan.scan_service import scan_api

base_api_url_scan = Blueprint('base_api_url_scan', __name__)

@base_api_url_scan.route('', methods=['POST'])
@bearer_token_required
def scan():
    data = request.json
    responses = scan_api(data)
    return ResponseHandler.success_without_message(responses)

@base_api_url_scan.route('/second', methods=['POST'])
@bearer_token_required
def scan_second():
    data = request.json
    responses = scan_api_2(data)
    return ResponseHandler.success_without_message(responses)

