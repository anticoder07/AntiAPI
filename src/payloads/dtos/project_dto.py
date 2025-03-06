from datetime import datetime


class ProjectDto:
    def __init__(self, data):
        self.project_id = data.get('project_id', None)
        self.project_name = data.get('project_name', None)
        self.company_id = data.get('company_id', None)

        self.updated_at = data.get('updated_at', None)
        self.created_at = data.get('created_at', None)

        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "company_id": self.company_id,
            "project_name": self.project_name,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
