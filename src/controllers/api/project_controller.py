from flask import request, Blueprint

from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler
from src.services.project_service import create_project_service, get_projects_service, delete_project_service, \
    get_project_service, change_project_name_service

base_api_url_project = Blueprint('base_api_url_project', __name__)


@base_api_url_project.route('', methods=['POST'])
@bearer_token_required
def create_new_project():
    data = request.json
    project = create_project_service(data)
    return ResponseHandler.success_without_message(project.to_dict())


@base_api_url_project.route('', methods=['GET'])
@bearer_token_required
def take_projects():
    pid = request.args.get('id')

    projects = get_project_service(pid) if pid else get_projects_service()

    return ResponseHandler.success_without_message(projects)

@base_api_url_project.route('', methods=['PATCH'])
@bearer_token_required
def change_project_name():
    data = request.json
    project = change_project_name_service(data)
    return ResponseHandler.success_without_message(project)

@base_api_url_project.route('', methods=['DELETE'])
@bearer_token_required
def delete_project():
    data = request.json
    msg = delete_project_service(data)
    return ResponseHandler.success(msg)
