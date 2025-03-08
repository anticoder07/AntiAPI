from http import HTTPStatus

from flask import g

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.models.payload import db
from src.payloads.dtos.project_dto import ProjectDto
from src.repositories.api_repository import delete_api_by_topic_id
from src.repositories.project_repository import get_projects_by_company_id, \
    get_project_by_project_id, delete_project_by_project_id, save_project, update_project_name
from src.repositories.topic_repository import delete_topic_by_project_id, get_topic_ids_by_project_id


def create_project_service(data):
    validate_project_name(data)

    new_project = save_project(
        data.get('project_name'),
        g.company_id,
    )

    project_dto = ProjectDto(new_project.to_dict())

    return project_dto


def change_project_name_service(data):
    if data.get('project_id') is None:
        raise CustomException("project_id cannot null", HTTPStatus.BAD_REQUEST)
    validate_project_name(data)

    company_id = g.company_id
    project = get_project_by_project_id(data.get('project_id'))
    if project is None or int(project.company_id) != int(company_id):
        raise CustomException("project not found", HTTPStatus.NOT_FOUND)

    project_new = update_project_name(data.get('project_id'), data.get('project_name'))

    return ProjectDto(project_new.to_dict())


def get_projects_service():
    company_id = g.company_id

    project_list = get_projects_by_company_id(company_id)

    project_dto_list = []
    for project in project_list:
        project_dto_list.append(ProjectDto(project.to_dict()).to_dict())

    return project_dto_list


def get_project_service(pid):
    company_id = g.company_id

    project = get_project_by_project_id(pid)

    if int(project.company_id) != int(company_id):
        raise CustomException('Project authorization', HTTPStatus.UNAUTHORIZED)

    return ProjectDto(project.to_dict()).to_dict()


def delete_project_service(data):
    project_id = data.get('project_id')
    if project_id is None:
        raise CustomException("projectId cannot null", HTTPStatus.BAD_REQUEST)

    company_id = g.company_id
    project = get_project_by_project_id(project_id)
    if project is None or int(project.company_id) != int(company_id):
        raise CustomException("project not found", HTTPStatus.NOT_FOUND)

    try:
        with db.session.begin():
            if not delete_project_by_project_id(project_id):
                raise CustomException("project cannot be deleted", HTTPStatus.BAD_REQUEST)

            topic_ids = get_topic_ids_by_project_id(project_id)

            if not delete_topic_by_project_id(project_id):
                raise CustomException("project cannot be deleted", HTTPStatus.BAD_REQUEST)

            for topic_id in topic_ids:
                if not delete_api_by_topic_id(topic_id):
                    raise CustomException("topic cannot be deleted", HTTPStatus.BAD_REQUEST)

        return "deleted project successfully"

    except Exception as e:
        db.session.rollback()
        raise CustomException(f"Unexpected error: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR)


def validate_project_name(data):
    project_name = data.get('project_name')

    if not isinstance(project_name, str) or not project_name.strip():
        raise CustomException("Project name must be a non-empty string", HTTPStatus.BAD_REQUEST)
