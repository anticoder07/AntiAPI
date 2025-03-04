from flask import Blueprint, request, jsonify

base_api_url = Blueprint('base_api_url', __name__)


@base_api_url.route('/auth/login', methods=['POST'])
def login_page():
    data = request.json
    print(data)

    return jsonify({"status": "success", "message": "Login request received"}), 200