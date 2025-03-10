from http import HTTPStatus

from flask import g

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.payloads.dtos.vul_dto import VulDto
from src.repositories.api_repository import get_api_ids_by_topic_id, get_api_by_api_id
from src.repositories.project_repository import get_project_by_project_id
from src.repositories.topic_repository import get_topic_ids_by_project_id, get_topic_by_topic_id
from src.repositories.vul_repository import get_vuls_by_api_id

def get_vuls_project(project_id):
    if project_id is None:
        raise CustomException("project_id cannot be None", HTTPStatus.BAD_REQUEST)

    project = get_project_by_project_id(project_id)
    if project is None:
        raise CustomException("project_id cannot be None", HTTPStatus.BAD_REQUEST)
    if str(project.company_id) != str(g.company_id):
        raise CustomException("project not found", HTTPStatus.NOT_FOUND)

    vuls = []

    topics_id = get_topic_ids_by_project_id(project_id)
    for topic_id in topics_id:
        apis_id = get_api_ids_by_topic_id(topic_id)
        for api_id in apis_id:
            vuls_list = get_vuls_by_api_id(api_id)
            for vul in vuls_list:
                vuls.append(VulDto(vul.to_dict()).to_dict())

    return vuls

def get_vuls_api(api_id):
    if api_id is None:
        raise CustomException("api_id cannot be None", HTTPStatus.BAD_REQUEST)

    api = get_api_by_api_id(api_id)
    if api is None:
        raise CustomException("api not found", HTTPStatus.NOT_FOUND)

    topic = get_topic_by_topic_id(api.topic_id)
    project = get_project_by_project_id(topic.project_id)
    if str(project.company_id) != str(g.company_id):
        raise CustomException("project not found", HTTPStatus.NOT_FOUND)

    vuls_res = []
    vuls_list = get_vuls_by_api_id(api_id)
    for vul in vuls_list:
        vuls_res.append(VulDto(vul.to_dict()).to_dict())

    return vuls_res
