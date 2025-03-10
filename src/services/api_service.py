import base64
import json
from http import HTTPStatus

from flask import g

from src.commons.database.mySql.config_connect_my_sql import db
from src.commons.exception.custom_exception.custom_exception import CustomException
from src.payloads.dtos.api_dto import ApiDto
from src.repositories.api_repository import create_api, delete_api_by_api_id, get_api_by_api_id, get_apis_by_topic_id
from src.repositories.project_repository import get_project_by_project_id
from src.repositories.topic_repository import get_topic_by_topic_id, get_topic_ids_by_project_id


def create_new_api_service(data):
    topic_id = data.get("topic_id")
    api_name = data.get("api_name")
    api_type = data.get("api_type")
    format_api = decode_base64_to_string(data.get("format_api"))
    endpoint = data.get("endpoint")
    if topic_id is None or api_name is None or api_type is None or format_api is None or endpoint is None:
        raise CustomException("Input field cannot be empty", HTTPStatus.BAD_REQUEST)

    line = validate_api_format(format_api)
    if line != -1:
        raise CustomException("Format scan wrong in line: " + str(line), HTTPStatus.BAD_REQUEST)

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

        return "deleted scan successfully"

    except Exception as e:
        db.session.rollback()
        raise CustomException(f"Unexpected error: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR)


def validate_api_format(json_string):
    try:
        # Split JSON string into lines for line number tracking
        lines = json_string.strip().split('\n')

        # Parse JSON
        data = json.loads(json_string)

        # Check that data is a dictionary
        if not isinstance(data, dict):
            return 1

        # Validate path_variable if it exists
        if "path_variable" in data:
            if not isinstance(data["path_variable"], list):
                line_num = find_line_number(lines, '"path_variable"')
                return line_num

            for i, item in enumerate(data["path_variable"]):
                if not isinstance(item, dict):
                    line_num = find_element_line(lines, "path_variable", i)
                    return line_num

                # Check required fields for path_variable items
                required_fields = ["type", "default_value"]
                for field in required_fields:
                    if field not in item:
                        line_num = find_element_line(lines, "path_variable", i)
                        return line_num

                # Check default_value is a list
                if not isinstance(item["default_value"], list):
                    line_num = find_line_number(lines, '"default_value"', find_element_line(lines, "path_variable", i))
                    return line_num

        # Validate arg if it exists
        if "arg" in data:
            if not isinstance(data["arg"], list):
                line_num = find_line_number(lines, '"arg"')
                return line_num

            for i, arg in enumerate(data["arg"]):
                if not isinstance(arg, dict):
                    line_num = find_element_line(lines, "arg", i)
                    return line_num

                required_arg_keys = ["arg_key", "arg_type", "default_value"]
                for key in required_arg_keys:
                    if key not in arg:
                        line_num = find_element_line(lines, "arg", i)
                        return line_num

                if not isinstance(arg["arg_key"], str):
                    line_num = find_line_number(lines, f'"arg_key"', find_element_line(lines, "arg", i))
                    return line_num

                if not isinstance(arg["arg_type"], str):
                    line_num = find_line_number(lines, f'"arg_type"', find_element_line(lines, "arg", i))
                    return line_num

                if not isinstance(arg["default_value"], list):
                    line_num = find_line_number(lines, f'"default_value"', find_element_line(lines, "arg", i))
                    return line_num

        # Validate body if it exists
        if "body" in data:
            if not isinstance(data["body"], dict):
                line_num = find_line_number(lines, '"body"')
                return line_num

            result = validate_body_structure(data["body"], lines, "body")
            if result != -1:
                return result

        # If no errors, return -1
        return -1

    except json.JSONDecodeError as e:
        # Return line with JSON syntax error
        return e.lineno
    except Exception:
        # If there's another error, return line 1
        return 1


def validate_body_structure(body, lines, path):
    for key, value in body.items():
        line_num = find_line_number(lines, f'"{key}"', find_line_number(lines, f'"{path}"'))

        # Check if value is an object
        if not isinstance(value, dict):
            return line_num

        # Check for required 'type' property
        if "type" not in value:
            return line_num

        if not isinstance(value["type"], str):
            return find_line_number(lines, '"type"', line_num)

        # If there's a default_value, it should be a list
        if "default_value" in value and not isinstance(value["default_value"], list):
            return find_line_number(lines, '"default_value"', line_num)

        # Check if it's an array
        if value["type"] == "array":
            if "items" not in value:
                return line_num

            items = value["items"]
            items_line = find_line_number(lines, '"items"', line_num)

            if isinstance(items, str):
                # String items are accepted
                pass
            elif isinstance(items, dict):
                # Check object structure
                if "type" not in items:
                    return items_line

                if items["type"] == "object":
                    if "properties" not in items:
                        return items_line

                    # Validate properties of the object items
                    for prop_key, prop_val in items["properties"].items():
                        prop_line = find_line_number(lines, f'"{prop_key}"', items_line)

                        if not isinstance(prop_val, dict):
                            return prop_line

                        if "type" not in prop_val:
                            return prop_line

                        if not isinstance(prop_val["type"], str):
                            return find_line_number(lines, '"type"', prop_line)

                        # If there's a default_value, it should be a list
                        if "default_value" in prop_val and not isinstance(prop_val["default_value"], list):
                            return find_line_number(lines, '"default_value"', prop_line)
            else:
                return items_line

    return -1


def find_line_number(lines, pattern, start_line=0):
    for i in range(start_line, len(lines)):
        if pattern in lines[i]:
            return i + 1  # Return line number (starting from 1)
    return -1


def find_element_line(lines, array_name, index):
    # Find the line of the element at the given index in the array
    array_start = find_line_number(lines, f'"{array_name}"')
    if array_start == -1:
        return 1

    # Count opening brackets to identify the element at the given index
    bracket_count = 0
    brace_count = 0
    current_index = -1

    for i in range(array_start, len(lines)):
        line = lines[i]

        # Count opening and closing brackets
        for char in line:
            if char == '[':
                bracket_count += 1
                if bracket_count == 1 and brace_count == 0:
                    current_index = -1
            elif char == ']':
                bracket_count -= 1
            elif char == '{' and bracket_count > 0:
                brace_count += 1
                if brace_count == 1:
                    current_index += 1
                    if current_index == index:
                        return i + 1
            elif char == '}' and bracket_count > 0:
                brace_count -= 1

    return array_start


def decode_base64_to_string(base64_string, encoding='utf-8'):
    try:
        decoded_bytes = base64.b64decode(base64_string)
        decoded_string = decoded_bytes.decode(encoding)
        return decoded_string
    except Exception as e:
        raise CustomException("Error with message: " + str(e), HTTPStatus.INTERNAL_SERVER_ERROR)


def get_apis_by_project_id(project_id):
    topic_ids = get_topic_ids_by_project_id(project_id)

    apis = []
    for topic_id in topic_ids:
        apis.extend(get_apis_by_topic_id(topic_id))

    return apis
