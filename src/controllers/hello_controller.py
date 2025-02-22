from flask import Blueprint

from src.commons.payload.response_handler import ResponseHandler
from src.services.message_service import MessageService

hello_bp = Blueprint('hello', __name__)
message_service = MessageService()

@hello_bp.route('/greeting', methods=['GET'])
def get_greeting():
    message = message_service.get_greeting()
    return ResponseHandler.success(ResponseHandler.STATUS_SUCCESS, message.to_dict())
