from http import HTTPStatus

from flask import g

from src.commons.database.mySql.config_connect_my_sql import db
from src.commons.exception.custom_exception.custom_exception import CustomException
from src.payloads.dtos.api_dto import ApiDto
from src.repositories.api_repository import create_api, delete_api_by_api_id, get_api_by_api_id, get_apis_by_topic_id
from src.repositories.project_repository import get_project_by_project_id
from src.repositories.topic_repository import get_topic_by_topic_id


def create_new_api_service(data):
    topic_id = data.get("topic_id")
    api_name = data.get("api_name")
    api_type = data.get("api_type")
    format_api = data.get("format_api")
    endpoint = data.get("endpoint")
    if topic_id is None or api_name is None or api_type is None or format_api is None or endpoint is None:
        raise CustomException("Input field cannot be empty", HTTPStatus.BAD_REQUEST)

    topic = get_topic_by_topic_id(topic_id)
    if topic is None:
        raise CustomException("Topic not found", HTTPStatus.NOT_FOUND)

    api_new = create_api(
        topic_id=topic_id,
        api_name=api_name,
        api_type=api_type,
        format_api=format_api,
        endpoint=endpoint,
    )

    return ApiDto(api_new.to_dict())


def get_apis_service(topic_id):
    if topic_id is None:
        raise CustomException("Input field cannot be empty", HTTPStatus.BAD_REQUEST)

    topic = get_topic_by_topic_id(topic_id)
    if topic is None:
        raise CustomException("Topic not found", HTTPStatus.NOT_FOUND)

    api_list = get_apis_by_topic_id(topic_id)
    api_dto_list = []
    for api in api_list:
        api_dto_list.append(ApiDto(api.to_dict()).to_dict())

    return api_dto_list


def get_api_service(api_id):
    if api_id is None:
        raise CustomException("api_id cannot null", HTTPStatus.BAD_REQUEST)

    api = get_api_by_api_id(api_id)
    if api is None:
        raise CustomException("Api does not exist", HTTPStatus.NOT_FOUND)

    topic = get_topic_by_topic_id(api.topic_id)
    if topic is None:
        raise CustomException("Topic not found", HTTPStatus.NOT_FOUND)

    project = get_project_by_project_id(topic.project_id)
    if project is None:
        raise CustomException("Project not found", HTTPStatus.NOT_FOUND)

    if int(project.company_id) != int(g.company_id):
        raise CustomException("Api unauthorized", HTTPStatus.UNAUTHORIZED)

    return ApiDto(api.to_dict())


def delete_api_service(data):
    api_id = data.get("api_id")
    if api_id is None:
        raise CustomException("api_id cannot null", HTTPStatus.BAD_REQUEST)

    api = get_api_by_api_id(api_id)
    if api is None:
        raise CustomException("Api does not exist", HTTPStatus.NOT_FOUND)

    topic = get_topic_by_topic_id(api.topic_id)
    if topic is None:
        raise CustomException("Topic not found", HTTPStatus.NOT_FOUND)

    project = get_project_by_project_id(topic.project_id)
    if project is None:
        raise CustomException("Project not found", HTTPStatus.NOT_FOUND)

    if int(project.company_id) != int(g.company_id):
        raise CustomException("Api unauthorized", HTTPStatus.UNAUTHORIZED)

    try:
        if not delete_api_by_api_id(api_id):
            raise CustomException("Topic cannot be deleted", HTTPStatus.BAD_REQUEST)

        db.session.commit()

        return "deleted api successfully"

    except Exception as e:
        db.session.rollback()
        raise CustomException(f"Unexpected error: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR)
