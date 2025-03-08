from datetime import datetime


class ApiDto:
    def __init__(self, data):
        self.api_id = data.get('api_id', None)
        self.api_name = data.get('api_name', None)
        self.api_type = data.get('api_type', None)
        self.format_api = data.get('format_api', None)
        self.endpoint = data.get('endpoint', None)
        self.created_at = data.get('created_at', None)

        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "api_id": self.api_id,
            "api_name": self.api_name,
            "api_type": self.api_type,
            "format_api": self.format_api,
            "endpoint": self.endpoint,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }
