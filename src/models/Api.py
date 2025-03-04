from src.models.EApiType import EApiType


class Api:
    def __init__(self, api_id, topic_id, api_name, api_type: EApiType, format_api, endpoint):
        self.api_id = api_id
        self.topic_id = topic_id
        self.api_name = api_name
        self.api_type = api_type
        self.format_api = format_api
        self.endpoint = endpoint
