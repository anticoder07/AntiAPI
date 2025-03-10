from http import HTTPStatus

from flask import g

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.repositories.project_repository import get_project_by_project_id


def validate_scan(data):
    base_url = data.get("base_url")
    project_id = data.get("project_id")
    api_payloads = data.get("api_payload")

    if base_url is None:
        raise CustomException("base_url cannot be None", HTTPStatus.BAD_REQUEST)
    if project_id is None:
        raise CustomException("project_id cannot be None", HTTPStatus.BAD_REQUEST)

    project = get_project_by_project_id(project_id)
    if project is None or str(project.company_id) != str(g.company_id):
        raise CustomException("project_id is invalid or not accessible", HTTPStatus.BAD_REQUEST)

    return base_url, project_id, api_payloads
