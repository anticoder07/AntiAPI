from datetime import datetime

from src.commons.database.mySql.config_connect_my_sql import db


class Project(db.Model):
    __tablename__ = 'Project'

    project_id = db.Column('ProjectId', db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column('CompanyId', db.Integer, db.ForeignKey('Company.CompanyId'), nullable=False)
    project_name = db.Column('ProjectName', db.String(255), nullable=False)
    updated_at = db.Column('UpdateAt', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column('CreateAt', db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "company_id": self.company_id,
            "project_name": self.project_name,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }
