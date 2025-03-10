from datetime import datetime


class VulDto:
    def __init__(self, data):
        self.vul_id = data.get('vul_id', None)
        self.api_id = data.get('api_id', None)
        self.payload = data.get('payload', None)
        self.regex = data.get('regex', None)
        self.created_at = data.get('created_at', None)

        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "vul_id": self.vul_id,
            "api_id": self.api_id,
            "payload": self.payload,
            "regex": self.regex,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
