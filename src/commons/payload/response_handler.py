from flask import jsonify
from datetime import datetime, UTC
from http import HTTPStatus

class ResponseHandler:
    STATUS_SUCCESS = "SUCCESS"
    STATUS_ERROR = "ERROR"

    @staticmethod
    def generate_response(message, status, data=None, pagination=None, status_code=HTTPStatus.OK):
        response = {
            "status": status,
            "message": message,
            "data": data,
            "metadata": {
                "timestamp": datetime.now(UTC).isoformat()
            }
        }

        if pagination:
            response["metadata"]["pagination"] = {
                "page": pagination.get("page", 0),
                "size": pagination.get("size", 10),
                "nextPage": pagination.get("nextPage", False)
            }

        return jsonify(response), status_code

    @staticmethod
    def success(message="Operation completed successfully", data=None, pagination=None):
        return ResponseHandler.generate_response(message, ResponseHandler.STATUS_SUCCESS, data, pagination, HTTPStatus.OK)

    @staticmethod
    def error(message="An error occurred", status_code=HTTPStatus.INTERNAL_SERVER_ERROR):
        return ResponseHandler.generate_response(message, ResponseHandler.STATUS_ERROR, None, None, status_code)

    @staticmethod
    def error_from_exception(exception, status_code=HTTPStatus.INTERNAL_SERVER_ERROR):
        return ResponseHandler.error(str(exception), status_code)
