from src.commons.database.mySql.config_connect_my_sql import db
from src.models.payload import Payload


def get_all_payload():
    return db.session.query(Payload).all()
