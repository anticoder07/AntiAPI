from datetime import datetime

from src.commons.database.mySql.config_connect_my_sql import db
from src.models.topic import Topic


def create_topic(project_id, topic_name):
    new_topic = Topic(
        project_id=project_id,
        topic_name=topic_name,
        created_at=datetime.utcnow(),
    )

    Topic.query.session.add(new_topic)
    Topic.query.session.commit()
    return new_topic

def get_topic_by_topic_id(topic_id):
    return Topic.query.filter_by(topic_id=topic_id).first()

def get_topic_ids_by_project_id(project_id):
    return [topic_id for (topic_id,) in Topic.query.with_entities(Topic.topic_id).filter_by(project_id=project_id).all()]


def get_topic_by_project_id(project_id):
    return Topic.query.filter_by(project_id=project_id).all()

def update_topic_name(topic_id, topic_name):
    return Topic.query.filter_by(topic_id=topic_id).update({'topic_name': topic_name})

def delete_topic_by_topic_id(topic_id):
    return db.session.query(Topic).filter_by(topic_id=topic_id).delete()

def delete_topic_by_project_id(project_id):
    return db.session.query(Topic).filter_by(project_id=project_id).delete()