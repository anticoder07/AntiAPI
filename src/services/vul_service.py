import json
from http import HTTPStatus

import requests
from flask import g

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.repositories.api_repository import get_apis_by_topic_id
from src.repositories.payload_repository import get_all_payload
from src.repositories.project_repository import get_project_by_project_id
from src.repositories.topic_repository import get_topic_ids_by_project_id


def scan_vul(data):
    base_url = data['base_url']
    port = data['port']
    project_id = data['project_id']

    if base_url == '' or port == '' or project_id == '' or base_url is None or port is None or project_id is None:
        raise CustomException("Input field cannot be empty", HTTPStatus.BAD_REQUEST)

    project = get_project_by_project_id(project_id)
    if project is None:
        raise CustomException("Project not found", HTTPStatus.NOT_FOUND)
    if str(project.company_id) != g.company_id:
        raise CustomException("Project not found", HTTPStatus.NOT_FOUND)

    payload_model_list = get_all_payload()
    payload_list = []
    for payload in payload_model_list:
        payload_list.append(payload.payload_content)

    topic_id_list = get_topic_ids_by_project_id(project_id)
    api_list = []

    for topic_id in topic_id_list:
        api_list.append(get_apis_by_topic_id(topic_id))

    for api in api_list:
        format_api = json.loads(api.format_api)
        results_body = make_api_by_format_api(format_api, payload_list)
        results_endpoint = generate_api_variants(format_api, api.endpoint, payload_list)
        results_response = send_requests(base_url, port, results_endpoint, results_body, api.api_type)

        print(results_response)


def make_api_by_format_api(format_api, payload_list):
    body = format_api['body']
    results = []

    # Hàm đệ quy để tạo template dựa trên bất kỳ cấu trúc nào
    def generate_template(structure):
        if isinstance(structure, dict):
            if 'type' in structure:
                # Đây là một định nghĩa trường
                field_type = structure.get('type')

                if field_type == 'string':
                    return None  # Placeholder cho giá trị string

                elif field_type == 'array':
                    items = structure.get('items')
                    if isinstance(items, str):
                        # Mảng các giá trị đơn giản (vd: "String")
                        return []  # Placeholder cho mảng đơn giản
                    elif isinstance(items, dict):
                        # Mảng các object
                        item_template = generate_template(items)
                        return [item_template, item_template]  # Tạo 2 mẫu

                elif field_type == 'object':
                    # Object với properties
                    props = structure.get('properties', {})
                    obj_template = {}
                    for prop_key, prop_value in props.items():
                        obj_template[prop_key] = generate_template(prop_value)
                    return obj_template

            else:
                # Dictionary thông thường, xử lý từng key
                result = {}
                for key, value in structure.items():
                    result[key] = generate_template(value)
                return result

        return None  # Mặc định cho các trường hợp khác

    # Tạo template từ cấu trúc body
    template = {}
    for field_name, field_def in body.items():
        template[field_name] = generate_template(field_def)

    # Hàm để điền giá trị payload vào template
    def fill_template(template, payload_value):
        if template is None:
            return payload_value

        if isinstance(template, list):
            return [fill_template(item, payload_value) for item in template]

        if isinstance(template, dict):
            result = {}
            for key, value in template.items():
                result[key] = fill_template(value, payload_value)
            return result

        return payload_value

    # Tạo một instance cho mỗi giá trị payload
    for payload_item in payload_list:
        filled = fill_template(template, payload_item)
        results.append(filled)

    return results


def generate_api_variants(format_api, endpoint, payload_list):
    results = []

    # Lấy thông tin path variables và arguments
    path_variables = format_api.get("path_variable", [])
    arguments = format_api.get("arg", [])
    body = format_api.get("body", {})

    # Tạo template cho body
    def generate_body_template(body_structure):
        template = {}
        for field_name, field_def in body_structure.items():
            field_type = field_def.get('type')

            if field_type == 'string':
                template[field_name] = None  # Placeholder

            elif field_type == 'array':
                items = field_def.get('items')
                if isinstance(items, str):
                    # Mảng đơn giản
                    template[field_name] = []
                else:
                    # Mảng object
                    item_template = {}
                    for prop_key, prop_def in items.get('properties', {}).items():
                        item_template[prop_key] = None
                    template[field_name] = [item_template, item_template]  # 2 phần tử mẫu

        return template

    body_template = generate_body_template(body)

    # Hàm điền giá trị vào template
    def fill_template(template, value):
        if template is None:
            return value

        if isinstance(template, list):
            if not template:
                return [value]  # Mảng đơn giản
            else:
                # Mảng object
                result = []
                for item in template:
                    filled_item = {}
                    for key in item:
                        filled_item[key] = value
                    result.append(filled_item)
                return result

        if isinstance(template, dict):
            result = {}
            for key, val in template.items():
                result[key] = fill_template(val, value)
            return result

        return value

    # Tạo các biến thể cho mỗi giá trị payload
    for i, payload_item in enumerate(payload_list):
        # Thay thế path variables
        current_endpoint = endpoint
        for j, pv in enumerate(path_variables):
            placeholder = f"{{pv{j + 1}}}"
            if placeholder in current_endpoint:
                current_endpoint = current_endpoint.replace(placeholder, pv)

        # Tạo query params từ arguments
        query_params = []
        for arg in arguments:
            arg_key = arg.get("arg_key")
            arg_type = arg.get("arg_type")
            # Giả lập giá trị dựa trên kiểu
            if arg_type == "string":
                query_params.append(f"{arg_key}=sample_string_{i}")
            elif arg_type == "number":
                query_params.append(f"{arg_key}={i}")
            else:
                query_params.append(f"{arg_key}=sample_value_{i}")

        query_string = "?" + "&".join(query_params) if query_params else ""

        # Điền giá trị payload vào body
        filled_body = fill_template(body_template, payload_item)

        # Tạo variant hoàn chỉnh
        variant = {
            "endpoint": current_endpoint + query_string,
            "body": filled_body
        }

        results.append(variant)

    return results


def send_requests(base_url, port, results_endpoint, results_body, api_type):
    # Đảm bảo base_url không có dấu '/' ở cuối
    if base_url.endswith('/'):
        base_url = base_url[:-1]

    # Tạo URL đầy đủ
    base = f"{base_url}:{port}"

    responses = []

    # Duyệt qua từng endpoint và body tương ứng
    for i, (endpoint_data, body_data) in enumerate(zip(results_endpoint, results_body)):
        full_url = f"{base}{endpoint_data['endpoint']}"

        print(f"Sending {api_type} request to: {full_url}")

        try:
            # Thực hiện request dựa trên api_type
            if api_type.upper() == 'GET':
                response = requests.get(full_url)
            elif api_type.upper() == 'POST':
                response = requests.post(full_url, json=body_data)
            elif api_type.upper() == 'PUT':
                response = requests.put(full_url, json=body_data)
            elif api_type.upper() == 'DELETE':
                response = requests.delete(full_url)
            elif api_type.upper() == 'PATCH':
                response = requests.patch(full_url, json=body_data)
            else:
                print(f"Unsupported API type: {api_type}")
                continue

            # Lưu kết quả
            responses.append({
                'url': full_url,
                'method': api_type,
                'status_code': response.status_code,
                'response': response.json() if response.headers.get(
                    'content-type') == 'application/json' else response.text
            })

            print(f"Response status: {response.status_code}")

        except Exception as e:
            print(f"Error calling {full_url}: {str(e)}")
            responses.append({
                'url': full_url,
                'method': api_type,
                'error': str(e)
            })

    return responses
