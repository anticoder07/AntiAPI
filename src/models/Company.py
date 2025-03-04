from datetime import datetime

from src.models.ECompanyStatus import ECompanyStatus


class Company:
    def __init__(self, company_id, company_name, user_name, password, status: ECompanyStatus, created_at, content):
        self.company_id = company_id
        self.company_name = company_name
        self.user_name = user_name
        self.password = password
        self.status = status
        self.created_at = created_at
        self.content = content

    def to_dict(self):
        return {
            "companyName": self.company_name,
            "userName": self.user_name,
            "password": self.password,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "content": self.content
        }
