import re
from typing import List, Dict, Any, Tuple


def get_element_count(format_api: Dict) -> int:
    count = 0

    # Đếm path variables
    if "path_variable" in format_api:
        count += len(format_api["path_variable"])

    # Đếm arguments
    if "arg" in format_api:
        count += len(format_api["arg"])

    # Đếm các trường trong body
    if "body" in format_api:
        for key, value in format_api["body"].items():
            if isinstance(value, dict):
                if "type" in value and value["type"] != "array" and value["type"] != "object":
                    count += 1
                elif "type" in value and value["type"] == "array" and "items" in value:
                    if isinstance(value["items"], str):
                        count += 1  # Đơn giản là một mảng các giá trị đơn
                    elif isinstance(value["items"], dict) and "properties" in value["items"]:
                        # Mảng các đối tượng phức tạp
                        for prop_key, prop_value in value["items"]["properties"].items():
                            count += 1
            elif isinstance(value, list):
                count += len(value)

    return count


def get_default_values(format_api: Dict) -> List:
    default_values = []

    # Lấy default values từ path variables
    if "path_variable" in format_api:
        for path_var in format_api["path_variable"]:
            if "default_value" in path_var:
                default_values.append(path_var["default_value"])
            else:
                default_values.append(None)

    # Lấy default values từ arguments
    if "arg" in format_api:
        for arg in format_api["arg"]:
            if "default_value" in arg:
                default_values.append(arg["default_value"])
            else:
                default_values.append(None)

    # Lấy default values từ body
    if "body" in format_api:
        for key, value in format_api["body"].items():
            if isinstance(value, dict):
                if "default_value" in value:
                    default_values.append(value["default_value"])
                else:
                    default_values.append(None)

                # Xử lý các trường nested
                if "type" in value and value["type"] == "array" and "items" in value:
                    if isinstance(value["items"], dict) and "properties" in value["items"]:
                        for prop_key, prop_value in value["items"]["properties"].items():
                            if "default_value" in prop_value:
                                default_values.append(prop_value["default_value"])
                            else:
                                default_values.append(None)

    return default_values


def get_element_names(format_api: Dict) -> List[str]:
    element_names = []

    # Lấy tên từ path variables
    if "path_variable" in format_api:
        for i, path_var in enumerate(format_api["path_variable"]):
            element_names.append(f"path_variable_{i}")

    # Lấy tên từ arguments
    if "arg" in format_api:
        for arg in format_api["arg"]:
            if "arg_key" in arg:
                element_names.append(f"arg_{arg['arg_key']}")
            else:
                element_names.append(f"arg_unknown")

    # Lấy tên từ body
    if "body" in format_api:
        for key, value in format_api["body"].items():
            element_names.append(f"body_{key}")

            # Xử lý các trường nested
            if isinstance(value, dict) and "type" in value and value["type"] == "array" and "items" in value:
                if isinstance(value["items"], dict) and "properties" in value["items"]:
                    for prop_key in value["items"]["properties"].keys():
                        element_names.append(f"body_{key}_{prop_key}")

    return element_names


def get_element_type(format_api: Dict) -> List[str]:
    """
    Extracts the type of each element from the format_api structure.

    Args:
        format_api: Dictionary containing the API format specification

    Returns:
        List of element types corresponding to each element in the API
    """
    element_types = []

    # Get types from path variables
    if "path_variable" in format_api:
        for path_var in format_api["path_variable"]:
            if "type" in path_var:
                element_types.append(path_var["type"])
            else:
                element_types.append("Unknown")

    # Get types from arguments
    if "arg" in format_api:
        for arg in format_api["arg"]:
            if "arg_type" in arg:
                element_types.append(arg["arg_type"])
            else:
                element_types.append("Unknown")

    # Get types from body
    if "body" in format_api:
        for key, value in format_api["body"].items():
            if isinstance(value, dict):
                if "type" in value:
                    if value["type"] != "array" and value["type"] != "object":
                        # Simple field
                        element_types.append(value["type"])
                    elif value["type"] == "array" and "items" in value:
                        if isinstance(value["items"], str):
                            # Simple array
                            element_types.append(f"array<{value['items']}>")
                        elif isinstance(value["items"], dict) and "properties" in value["items"]:
                            # Array of complex objects
                            for prop_key, prop_value in value["items"]["properties"].items():
                                if "type" in prop_value:
                                    element_types.append(prop_value["type"])
                                else:
                                    element_types.append("Unknown")
                else:
                    element_types.append("Unknown")
            elif isinstance(value, list):
                for item in value:
                    element_types.append("Unknown")

    return element_types


def replace_path_variables(endpoint: str, path_vars: List[Any]) -> str:
    pattern = r'\{[^{}]*\}'
    matches = re.findall(pattern, endpoint)

    result = endpoint
    for i, match in enumerate(matches):
        if i < len(path_vars):
            result = result.replace(match, str(path_vars[i]), 1)

    return result


def build_api_request(datas: List, endpoint: str, format_api: Dict) -> Tuple[str, Dict]:
    data_index = 0
    path_vars = []
    query_params = {}
    body_request = {}

    # Xử lý path variables
    if "path_variable" in format_api:
        for i, path_var in enumerate(format_api["path_variable"]):
            if data_index < len(datas):
                path_vars.append(datas[data_index])
                data_index += 1
            else:
                # Sử dụng giá trị mặc định nếu có
                if "default_value" in path_var and isinstance(path_var["default_value"], list) and len(
                        path_var["default_value"]) > 0:
                    path_vars.append(path_var["default_value"][0])
                else:
                    path_vars.append("")

    # Xử lý arguments (query parameters)
    if "arg" in format_api:
        for arg in format_api["arg"]:
            if "arg_key" in arg:
                if data_index < len(datas):
                    query_params[arg["arg_key"]] = datas[data_index]
                    data_index += 1
                else:
                    # Sử dụng giá trị mặc định nếu có
                    if "default_value" in arg and isinstance(arg["default_value"], list) and len(
                            arg["default_value"]) > 0:
                        query_params[arg["arg_key"]] = arg["default_value"][0]

    # Xử lý body
    if "body" in format_api:
        for key, value in format_api["body"].items():
            if isinstance(value, dict):
                if "type" in value:
                    if value["type"] != "array" and value["type"] != "object":
                        # Trường dữ liệu đơn giản
                        if data_index < len(datas):
                            body_request[key] = datas[data_index]
                            data_index += 1
                        else:
                            # Sử dụng giá trị mặc định nếu có
                            if "default_value" in value and isinstance(value["default_value"], list) and len(
                                    value["default_value"]) > 0:
                                body_request[key] = value["default_value"][0]
                    elif value["type"] == "array" and "items" in value:
                        if isinstance(value["items"], str):
                            # Mảng đơn giản
                            if data_index < len(datas):
                                if isinstance(datas[data_index], list):
                                    body_request[key] = datas[data_index]
                                else:
                                    body_request[key] = [datas[data_index]]
                                data_index += 1
                            else:
                                body_request[key] = []
                        elif isinstance(value["items"], dict) and "properties" in value["items"]:
                            # Mảng các đối tượng phức tạp
                            array_items = []
                            item_obj = {}

                            for prop_key, prop_value in value["items"]["properties"].items():
                                if data_index < len(datas):
                                    item_obj[prop_key] = datas[data_index]
                                    data_index += 1
                                else:
                                    # Sử dụng giá trị mặc định nếu có
                                    if "default_value" in prop_value and isinstance(prop_value["default_value"],
                                                                                    list) and len(
                                        prop_value["default_value"]) > 0:
                                        item_obj[prop_key] = prop_value["default_value"][0]
                                    else:
                                        item_obj[prop_key] = None

                            array_items.append(item_obj)
                            body_request[key] = array_items

    # Xây dựng endpoint với path variables
    final_endpoint = replace_path_variables(endpoint, path_vars)

    # Thêm query parameters vào endpoint
    if query_params:
        query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
        final_endpoint = f"{final_endpoint}?{query_string}"

    return final_endpoint, body_request
