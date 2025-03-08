from datetime import datetime

from src.commons.database.mySql.config_connect_my_sql import db


class Api(db.Model):
    __tablename__ = 'Api'

    api_id = db.Column('ApiId', db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column('TopicId', db.Integer, db.ForeignKey('Topic.TopicId'), nullable=False)
    api_name = db.Column('ApiName', db.String(255), nullable=False)
    api_type = db.Column('ApiType', db.String(255), nullable=False)
    format_api = db.Column('FormatApi', db.Text, nullable=False)
    endpoint = db.Column('Endpoint', db.String(255), nullable=False)
    created_at = db.Column('CreateAt', db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "api_id": self.api_id,
            "topic_id": self.topic_id,
            "api_name": self.api_name,
            "api_type": self.api_type,
            "format_api": self.format_api,
            "endpoint": self.endpoint,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }
