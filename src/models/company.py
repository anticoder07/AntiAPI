from datetime import datetime
from src.commons.database.mySql.config_connect_my_sql import db

class Company(db.Model):
    __tablename__ = 'Company'

    company_id = db.Column('CompanyId', db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column('CompanyName', db.String(255), nullable=False)
    user_name = db.Column('Username', db.String(255), unique=True, nullable=False)
    password = db.Column('Password', db.String(255), nullable=False)
    status = db.Column('Status', db.String(255), nullable=False)
    created_at = db.Column('CreateAt', db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "user_name": self.user_name,
            "password": self.password,
            "status": self.status,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
