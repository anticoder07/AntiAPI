from flask import Blueprint

from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler
from src.services.company_service import get_company_profile

base_api_url_company = Blueprint('base_api_url_company', __name__)


@base_api_url_company.route('', methods=['GET'])
@bearer_token_required
def take_company_profile():
    company_profile = get_company_profile()
    return ResponseHandler.success_without_message(company_profile)
