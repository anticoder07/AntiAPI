from datetime import datetime
from src.commons.database.mySql.config_connect_my_sql import db
from src.models.e_customer_type import ECustomerType


class Token(db.Model):
    __tablename__ = 'Token'

    token_id = db.Column('TokenId', db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column('CustomerId', db.Integer, nullable=False)
    customer_type = db.Column('CustomerType', db.Enum(ECustomerType), nullable=False)
    token = db.Column('Token', db.String(1000), unique=True, nullable=False)
    expires_at = db.Column('ExpiresAt', db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "token_id": self.token_id,
            "customer_id": self.customer_id,
            "customer_type": self.customer_type.name if isinstance(self.customer_type, ECustomerType) else self.customer_type,
            "token": self.token,
            "expires_at": self.expires_at.isoformat() if isinstance(self.expires_at, datetime) else self.expires_at
        }
