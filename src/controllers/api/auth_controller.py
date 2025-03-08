from flask import request, g, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler
from src.services.auth.auth_service import create_account, login_company, log_out_company

base_api_url_auth = Blueprint('base_api_url_auth', __name__)


@base_api_url_auth.route('/sign-up', methods=['POST'])
def sign_up_controller():
    data = request.json
    return ResponseHandler.success_without_message(create_account(data))


@base_api_url_auth.route('/login', methods=['POST'])
def login_controller():
    data = request.json
    return ResponseHandler.success_without_message(login_company(data))


@base_api_url_auth.route('/log-out', methods=['POST'])
@bearer_token_required
def log_out_controller():
    auth_header = request.headers.get('Authorization')
    return ResponseHandler.success_without_message(log_out_company(auth_header).to_dict())


@base_api_url_auth.route('/ping', methods=['GET'])
@jwt_required()
def ping():
    try:
        current_user = get_jwt_identity()
        return {
            "message": "pong",
            "user_id": current_user
        }
    except Exception as e:
        print(f"Full error details: {str(e)}")
        return {
            "error": "Authentication failed",
            "details": str(e)
        }, 401


@base_api_url_auth.route('/ping-custom', methods=['GET'])
@bearer_token_required
def ping_custom():
    company_id = g.company_id
    return {
        "message": "pong",
        "user_id": company_id
    }
