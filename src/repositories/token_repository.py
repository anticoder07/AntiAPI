from src.commons.database.mySql.config_connect_my_sql import db
from src.models.token import Token


def save_token(customer_id, customer_type, token, expires_at):
    new_token = Token(
        customer_id=customer_id,
        customer_type=customer_type,
        expires_at=expires_at,
        token=token
    )

    db.session.add(new_token)
    db.session.commit()
    return new_token


def get_token_by_value(value):
    return Token.query.filter_by(token=value).first()
