import json
from http import HTTPStatus

import requests
from flask import g

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.repositories.api_repository import get_api_by_api_id
from src.repositories.project_repository import get_project_by_project_id, update_project_base_url
from src.repositories.topic_repository import get_topic_by_topic_id
from src.repositories.vul_repository import get_vuls
from src.services.protect.regex_service import validate_requests
from src.services.scan.format_api_handler_service import get_element_names


def enable_middleware(data):
    project_id = data['project_id']
    if project_id is None:
        raise CustomException('project_id is required', HTTPStatus.BAD_REQUEST)

    base_url = data['base_url']
    if base_url is None:
        raise CustomException('base_url is required', HTTPStatus.BAD_REQUEST)

    project = get_project_by_project_id(project_id)
    if project is None:
        raise CustomException('project_id is not found', HTTPStatus.NOT_FOUND)

    if str(project.project_id) != str(g.company_id):
        raise CustomException('project_id is not found', HTTPStatus.NOT_FOUND)

    update_project_base_url(project_id, base_url)

    return {"Enable middleware": True}


def disable_middleware(data):
    project_id = data['project_id']
    if project_id is None:
        raise CustomException('project_id is required', HTTPStatus.BAD_REQUEST)

    project = get_project_by_project_id(project_id)
    if project is None:
        raise CustomException('project_id is not found', HTTPStatus.NOT_FOUND)

    if str(project.project_id) != str(g.company_id):
        raise CustomException('project_id is not found', HTTPStatus.NOT_FOUND)

    update_project_base_url(project_id, None)

    return {"Disable middleware": True}


def handler_request(api_id, endpoint, body, http_method, full_request):
    api_id = int(api_id)
    if api_id is None:
        raise CustomException(HTTPStatus.BAD_REQUEST, "api_id")
    api = get_api_by_api_id(int(api_id))
    if api is None:
        raise CustomException("Http not found", HTTPStatus.NOT_FOUND)

    topic_id = get_topic_by_topic_id(api.topic_id)
    topic = get_topic_by_topic_id(topic_id)
    project = get_project_by_project_id(topic.project_id)
    base_url = project.base_url
    if base_url is None:
        raise CustomException('Service not run', HTTPStatus.BAD_REQUEST)

    format_api = json.loads(api.format_api)
    endpoint_api = api.endpoint
    vuls = get_vuls(api_id)

    types = get_element_names(format_api)

    print(endpoint)

    args = {}
    if '?' in endpoint:
        endpoint_path, query_string = endpoint.split('?', 1)
        query_params = query_string.split('&')
        for param in query_params:
            if '=' in param:
                key, value = param.split('=', 1)
                import urllib.parse
                args[key] = urllib.parse.unquote(value)
    else:
        endpoint_path = endpoint

    path_parts = endpoint_path.split('/')
    path_parts = [p for p in path_parts if p]

    api_path_parts = endpoint_api.split('/')
    api_path_parts = [p for p in api_path_parts if p]

    path_variables = {}
    for i, part in enumerate(api_path_parts):
        if part.startswith('{') and part.endswith('}'):
            var_name = part[1:-1]
            if i < len(path_parts):
                if '_' in var_name:
                    prefix, suffix = var_name.split('_', 1)
                    if prefix not in path_variables:
                        path_variables[prefix] = {}
                    path_variables[prefix][suffix] = path_parts[i]
                else:
                    path_variables[var_name] = path_parts[i]

    for vul in vuls:
        if int(vul.cnt) < len(types):
            parts = types[int(vul.cnt)].split("_", 1)
            type_request = parts[0]
            type_key = parts[1]

            if type_request == "body":
                if body and type_key in body:
                    if not validate_requests(body[type_key], vul.regex):
                        raise CustomException("Invalid request body", HTTPStatus.BAD_REQUEST)
            elif type_request == "arg":
                if type_key in args:
                    if not validate_requests(args[type_key], vul.regex):
                        raise CustomException("Invalid query parameter", HTTPStatus.BAD_REQUEST)
            elif type_request == "path":
                if '_' in type_key:
                    prefix, suffix = type_key.split('_', 1)
                    if prefix in path_variables and isinstance(path_variables[prefix], dict) and suffix in \
                            path_variables[prefix]:
                        if not validate_requests(path_variables[prefix][suffix], vul.regex):
                            raise CustomException("Invalid path parameter", HTTPStatus.BAD_REQUEST)
                else:
                    if type_key in path_variables:
                        if not validate_requests(path_variables[type_key], vul.regex):
                            raise CustomException("Invalid path parameter", HTTPStatus.BAD_REQUEST)

    return send_request(http_method, endpoint, full_request, base_url)


def send_request(method, endpoint, full_request, base_url):
    url = f"{base_url}/{endpoint}"

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=full_request["headers"],
            params=full_request["query_params"],
            json=full_request["body"],
            files=full_request["files"],
            timeout=30
        )
        return response.json(), response.status_code

    except requests.Timeout:
        raise Exception("Request timed out after 30 seconds")

    except requests.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
