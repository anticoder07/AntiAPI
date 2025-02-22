import http

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.models.message import Message
from src.repositories.messageRepository import MessageRepository


class MessageService:
    def __init__(self):
        self.repository = MessageRepository()

    def get_greeting(self):
        message_content = self.repository.get_message()

        raise CustomException("Error", http.HTTPStatus.INTERNAL_SERVER_ERROR)
        return Message(message_content)
