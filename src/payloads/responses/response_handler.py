from datetime import datetime, timezone  # Chỉnh sửa UTC thành timezone để đúng cú pháp
from http import HTTPStatus

from flask import jsonify


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
                "timestamp": datetime.now(timezone.utc).isoformat()  # Đảm bảo UTC time zone
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
        return ResponseHandler.generate_response(message, ResponseHandler.STATUS_SUCCESS,
                                                 data.to_dict() if data else None, pagination, HTTPStatus.OK)

    @staticmethod
    def success_without_message(data=None, pagination=None):
        message = "Operation completed successfully"

        processed_data = data.to_dict() if hasattr(data, 'to_dict') else data

        return ResponseHandler.generate_response(
            message,
            ResponseHandler.STATUS_SUCCESS,
            processed_data,
            pagination,
            HTTPStatus.OK
        )
    @staticmethod
    def error(message="An error occurred", status_code=HTTPStatus.INTERNAL_SERVER_ERROR):
        return ResponseHandler.generate_response(message, ResponseHandler.STATUS_ERROR, None, None, status_code)

    @staticmethod
    def error_from_exception(exception, status_code=HTTPStatus.INTERNAL_SERVER_ERROR):
        return ResponseHandler.error(str(exception), status_code)


class BaseDto:
    def to_dict(self):
        if isinstance(self, dict):
            return self
        return {key: value for key, value in self.__dict__.items()}
