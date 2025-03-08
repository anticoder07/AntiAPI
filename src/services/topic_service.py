from http import HTTPStatus

from flask import g

from src.commons.database.mySql.config_connect_my_sql import db
from src.commons.exception.custom_exception.custom_exception import CustomException
from src.payloads.dtos.topic_dto import TopicDto
from src.repositories.api_repository import delete_api_by_topic_id
from src.repositories.project_repository import get_project_by_project_id
from src.repositories.topic_repository import (
    create_topic,
    get_topic_by_topic_id,
    update_topic_name,
    delete_topic_by_topic_id, get_topic_by_project_id
)


def validate_not_empty(value, field_name, status_code=HTTPStatus.BAD_REQUEST):
    if value is None or (isinstance(value, str) and str(value).strip() == ''):
        raise CustomException(f'{field_name} is required', status_code)


def validate_project_permission(project_id, company_id):
    project = get_project_by_project_id(project_id)
    if project is None or int(project.company_id) != int(company_id):
        raise CustomException('Project not found', HTTPStatus.NOT_FOUND)
    return project


def validate_topic_existence(topic_id):
    topic = get_topic_by_topic_id(topic_id)
    if topic is None:
        raise CustomException('Topic not found', HTTPStatus.NOT_FOUND)
    return topic


def create_topic_service(data):
    project_id = data['project_id']
    topic_name = data['topic_name']

    validate_not_empty(project_id, 'Project id')
    validate_not_empty(topic_name, 'Topic name')
    validate_project_permission(project_id, g.company_id)

    topic_new = create_topic(
        project_id=project_id,
        topic_name=topic_name
    )

    return TopicDto(topic_new.to_dict())


def take_topic_service(topic_id):
    validate_not_empty(topic_id, 'Topic id')
    company_id = g.company_id

    topic = validate_topic_existence(topic_id)
    validate_project_permission(topic.project_id, company_id)

    return TopicDto(topic.to_dict())


def take_topics_service(project_id):
    validate_not_empty(project_id, 'Project id')
    validate_project_permission(project_id, g.company_id)

    topic_list = get_topic_by_project_id(project_id)
    topic_dto_list = []
    for topic in topic_list:
        topic_dto_list.append(TopicDto(topic.to_dict()).to_dict())

    return topic_dto_list


def change_topic_name_service(data):
    topic_id = data['topic_id']
    topic_name = data['topic_name']

    validate_not_empty(topic_id, 'Topic id')
    validate_not_empty(topic_name, 'Topic name')
    company_id = g.company_id

    topic = validate_topic_existence(topic_id)
    validate_project_permission(topic.project_id, company_id)

    topic_new = update_topic_name(topic_id, topic_name)
    return TopicDto(topic_new.to_dict())


def delete_topic_service(data):
    topic_id = data['topic_id']
    validate_not_empty(topic_id, 'Topic id')

    topic = validate_topic_existence(topic_id)
    validate_project_permission(topic.project_id, g.company_id)

    try:
        if not delete_topic_by_topic_id(topic_id):
            raise CustomException("Topic cannot be deleted", HTTPStatus.BAD_REQUEST)

        if not delete_api_by_topic_id(topic_id):
            raise CustomException("topic cannot be deleted", HTTPStatus.BAD_REQUEST)

        db.session.commit()

        return "deleted topic successfully"

    except Exception as e:
        db.session.rollback()
        raise CustomException(f"Unexpected error: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR)
