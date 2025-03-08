from datetime import datetime


class TopicDto:
    def __init__(self, data):
        self.topic_id = data.get('topic_id', None)
        # self.project_id = data.get('project_id', None)
        self.topic_name = data.get('topic_name', None)

        self.updated_at = data.get('updated_at', None)
        self.created_at = data.get('created_at', None)

        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "topic_id": self.topic_id,
            # "project_id": self.project_id,
            "topic_name": self.topic_name,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
