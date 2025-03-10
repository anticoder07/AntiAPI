import json
from http import HTTPStatus

from flask import g

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.repositories.api_repository import create_api
from src.repositories.project_repository import get_project_by_project_id
from src.repositories.topic_repository import create_topic
from src.services.api_service import validate_api_format


def process_save_data(data, project_id):
    if project_id is None:
        raise CustomException(HTTPStatus.BAD_REQUEST, "Project ID is required")

    profile = get_project_by_project_id(project_id)
    if profile is None or str(profile.company_id) != str(g.company_id):
        raise CustomException("Project unauthorized", HTTPStatus.UNAUTHORIZED)

    topics_list = read_data_from_file(data)

    for topic in topics_list:
        topic_new = create_topic(
            project_id=project_id,
            topic_name=topic["topic_name"]
        )

        for api in topic["apis"]:
            line = validate_api_format(str(api.get('format_api')))
            if line != -1:
                raise CustomException("Format scan wrong in line: " + line, HTTPStatus.BAD_REQUEST)
            api_new = create_api(
                topic_new.topic_id,
                api.get('api_name'),
                api.get('api_type'),
                str(api.get('format_api')),
                api.get('endpoint')
            )

    return 'Successfully'


def read_data_from_file(data):
    topics_list = []

    if not isinstance(data, list):
        raise CustomException("Invalid JSON format", HTTPStatus.BAD_REQUEST)

    for project in data:
        topics = project.get('topics', [])
        for topic in topics:
            topic_name = topic.get('topic_name', 'Unknown')
            apis = topic.get('apis', [])

            topics_list.append({
                "topic_name": topic_name,
                "apis": apis
            })

    return topics_list


def process_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        topics = read_data_from_file(data)

        return topics

    except FileNotFoundError:
        raise CustomException("File not found", HTTPStatus.NOT_FOUND)

    except json.JSONDecodeError:
        raise CustomException("Invalid JSON file", HTTPStatus.BAD_REQUEST)

    except CustomException:
        raise CustomException("Invalid JSON file", HTTPStatus.BAD_REQUEST)

    except Exception as e:
        raise CustomException(f"An unexpected error occurred: {str(e)}",
                              HTTPStatus.INTERNAL_SERVER_ERROR)
