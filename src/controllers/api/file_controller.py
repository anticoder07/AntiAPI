import json
from http import HTTPStatus

from flask import Blueprint, request, jsonify

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler
from src.services.file_service import process_save_data

base_api_url_file = Blueprint('base_api_url_file', __name__)


@base_api_url_file.route('', methods=['POST'])
@bearer_token_required
def create_fast_topic_api():
    try:
        if 'file' not in request.files:
            return jsonify({"message": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"message": "Empty file"}), 400

        # Đọc và decode nội dung file
        file_content = file.read().decode('utf-8')
        data = json.loads(file_content)

        # Lấy project_id từ form data thay vì từ JSON body
        project_id = request.form.get('project_id')

        if not project_id:
            return jsonify({"message": "project_id is required"}), 400

        process_save_data(data, project_id)

        return ResponseHandler.success("Uploaded successfully", {})

    except json.JSONDecodeError:
        raise CustomException("Invalid JSON format in file", HTTPStatus.BAD_REQUEST)
    except Exception as e:
        raise CustomException(str(e), HTTPStatus.BAD_REQUEST)