from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Payload(db.Model):
    __tablename__ = 'Payload'

    payload_id = db.Column('PayloadId', db.Integer, primary_key=True, autoincrement=True)
    payload_content = db.Column('PayloadContent', db.Text, nullable=False)
    payload_type = db.Column('PayloadType', db.String(255), nullable=False)
    regex = db.Column('Regex', db.Text, nullable=True)
    language = db.Column('Language', db.String(50), nullable=False)
    created_at = db.Column('CreateAt', db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "payload_id": self.payload_id,
            "payload_content": self.payload_content,
            "payload_type": self.payload_type,
            "regex": self.regex,
            "language": self.language,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
