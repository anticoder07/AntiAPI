import json
from datetime import datetime

from src.commons.database.mySql.config_connect_my_sql import db
from src.models.vul import Vul


def create_vul(api_id, payload, regext_filter, cnt):
    if isinstance(payload, list):
        payload = json.dumps(payload)

    new_vul = Vul(
        api_id=api_id,
        payload=payload,
        regext=regext_filter,
        cnt = cnt,
        created_at=datetime.now()
    )

    db.session.add(new_vul)
    db.session.commit()
    return new_vul

def get_vuls(api_id):
    return db.session.query(Vul).filter(Vul.api_id == api_id).all()

def get_vuls_by_api_id(api_id):
    return db.session.query(Vul).filter(Vul.api_id == api_id).all()
