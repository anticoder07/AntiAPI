from flask import request, Blueprint

from src.commons.security.token_required import bearer_token_required
from src.payloads.responses.response_handler import ResponseHandler
from src.services.project_service import create_project, get_projects, delete_project_service, get_project

base_api_url_project = Blueprint('base_api_url_project', __name__)


@base_api_url_project.route('', methods=['POST'])
@bearer_token_required
def create_new_project():
    data = request.json
    project = create_project(data)
    return ResponseHandler.success_without_message(project.to_dict())


@base_api_url_project.route('', methods=['GET'])
@bearer_token_required
def take_projects():
    projects = get_projects()

    return ResponseHandler.success_without_message(projects)


@base_api_url_project.route('/single', methods=['GET'])
@bearer_token_required
def take_project():
    pid = request.args.get('id')
    projects = get_project(pid)

    return ResponseHandler.success_without_message(projects)


@base_api_url_project.route('', methods=['DELETE'])
def delete_project():
    data = request.json
    project = delete_project_service(data)
    return ResponseHandler.success(project)
