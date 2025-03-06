from datetime import datetime

from src.commons.database.mySql.config_connect_my_sql import db


class Topic(db.Model):
    __tablename__ = 'Topic'

    topic_id = db.Column('TopicId', db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column('ProjectId', db.Integer, db.ForeignKey('Project.ProjectId'), nullable=False)
    topic_name = db.Column('TopicName', db.String(255), nullable=False)
    update_at = db.Column('UpdateAt', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column('CreateAt', db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "topic_id": self.topic_id,
            "project_id": self.project_id,
            "topic_name": self.topic_name,
            "update_at": self.update_at.isoformat() if isinstance(self.update_at, datetime) else self.update_at,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }
