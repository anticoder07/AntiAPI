from datetime import datetime
from src.commons.database.mySql.config_connect_my_sql import db


class Vul(db.Model):
    __tablename__ = 'Vul'

    vul_id = db.Column('VulId', db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column('ApiId', db.Integer, db.ForeignKey('Api.ApiId'), nullable=False)  # Liên kết với Api
    payload = db.Column('Payload', db.Text, nullable=False)
    vul_type = db.Column('VulType', db.String(255), nullable=False)
    vul_status = db.Column('VulStatus', db.Integer, default=0)
    regex_fix = db.Column('RegexFix', db.Text, nullable=True)
    created_at = db.Column('CreateAt', db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "vul_id": self.vul_id,
            "api_id": self.api_id,
            "payload": self.payload,
            "vul_type": self.vul_type,
            "vul_status": self.vul_status,
            "regex_fix": self.regex_fix,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
