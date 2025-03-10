from datetime import datetime

from src.commons.database.mySql.config_connect_my_sql import db
from src.models.api import Api


def create_api(topic_id, api_name, api_type, format_api, endpoint):
    new_api = Api(
        topic_id=topic_id,
        api_name=api_name,
        api_type=api_type,
        format_api=format_api,
        endpoint=endpoint,
        created_at=datetime.utcnow()
    )
    db.session.add(new_api)
    db.session.commit()
    return new_api

def delete_api_by_api_id(api_id):
    return db.session.query(Api).filter(Api.api_id == api_id).delete()

def delete_api_by_topic_id(topic_id):
    return db.session.query(Api).filter(Api.topic_id == topic_id).delete()

def get_api_by_api_id(api_id):
    return db.session.query(Api).filter(Api.api_id == api_id).first()

def get_apis_by_topic_id(topic_id):
    return db.session.query(Api).filter(Api.topic_id == topic_id).all()

def get_api_ids_by_topic_id(topic_id):
    return [api.api_id for api in db.session.query(Api.api_id).filter(Api.topic_id == topic_id).all()]
