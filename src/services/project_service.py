from http import HTTPStatus

from flask import g

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.payloads.dtos.project_dto import ProjectDto
from src.repositories.company_repository import get_company_by_company_id
from src.repositories.project_repository import get_projects_by_company_id, \
    get_project_by_project_id, delete_project_by_project_id, save_project
from src.services.auth.password_service import hash_password, verify_password


def access_project(data):
    project_id = data['project_id']
    password = data['password']

    if project_id is not None or password is not None:
        raise CustomException('Project ID or Password is required', HTTPStatus.NOT_FOUND)

    project = get_project_by_project_id(project_id)
    if project_id is None:
        raise CustomException('Project ID is required', HTTPStatus.NOT_FOUND)

    if verify_password(password, project.get('password')) is False:
        raise CustomException('Password project is incorrect', HTTPStatus.BAD_REQUEST)

    return ProjectDto(project.to_dict())


def create_project(data):
    data['company_id'] = g.company_id
    validate_create_project(data)

    password = hash_password(data['password'])

    new_project = save_project(
        data.get('project_name'),
        g.company_id,
        password
    )

    project_dto = ProjectDto(new_project.to_dict())

    return project_dto


def get_projects():
    company_id = g.company_id

    project_list = get_projects_by_company_id(company_id)

    project_dto_list = []
    for project in project_list:
        project_dto_list.append(ProjectDto(project.to_dict()).to_dict())

    return project_dto_list


def delete_project_service(project_id):
    if project_id is None:
        raise CustomException("projectId cannot null", HTTPStatus.BAD_REQUEST)
    if get_project_by_project_id(project_id) is None:
        raise CustomException("project not found", HTTPStatus.NOT_FOUND)

    delete_project_by_project_id(project_id)

    return "deleted project successfully"


def validate_create_project(data):
    validate_company(data['company_id'])

    project_name = data.get('project_name')

    if not isinstance(project_name, str) or not project_name.strip():
        raise CustomException("Project name must be a non-empty string", HTTPStatus.BAD_REQUEST)


def validate_company(company_id):
    if company_id is None:
        raise CustomException("Company cannot null", HTTPStatus.BAD_REQUEST)
    if get_company_by_company_id(company_id) is None:
        raise CustomException("Company not found", HTTPStatus.NOT_FOUND)
