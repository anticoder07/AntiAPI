import json
import time
from http import HTTPStatus

import requests
from flask import g

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.repositories.api_repository import get_apis_by_topic_id
from src.repositories.payload_repository import get_all_payload
from src.repositories.project_repository import get_project_by_project_id
from src.repositories.topic_repository import get_topic_ids_by_project_id
from src.services.analysis_service import categorize_suspicious_responses
from src.services.api.format_api_handler_service import build_api_request, get_element_count
from src.services.api.scan_success_service import make_datas_payload_success


def make_datas_payload_vul(payload, format_api):
    count = get_element_count(format_api)

    datas = []
    for i in range(count):
        datas.append(payload)

    return datas


def scan_api(data):
    base_url = data.get("base_url")
    project_id = data.get("project_id")

    if base_url is None:
        raise CustomException("base_url cannot be None", HTTPStatus.BAD_REQUEST)
    if project_id is None:
        raise CustomException("project_id cannot be None", HTTPStatus.BAD_REQUEST)

    project = get_project_by_project_id(project_id)
    if project is None or str(project.company_id) != str(g.company_id):
        raise CustomException("project_id is invalid or not accessible", HTTPStatus.BAD_REQUEST)

    payload_models = get_all_payload()
    payloads = [payload.payload_content for payload in payload_models]

    topic_ids = get_topic_ids_by_project_id(project_id)
    apis = []
    for topic_id in topic_ids:
        apis.extend(get_apis_by_topic_id(topic_id))

    api_results = {}

    for api in apis:
        format_api = json.loads(api.format_api)
        endpoint_key = f"{api.api_type}:{api.endpoint}"

        if endpoint_key not in api_results:
            api_results[endpoint_key] = {
                "success_responses": [],
                "suspicious_responses": []
            }

        try:
            # First collect normal responses
            datas_success = make_datas_payload_success(format_api)
            for data in datas_success:
                final_endpoint_success, body_request_success = build_api_request(data, api.endpoint, format_api)
                rs = send_attack_request(api.api_type, base_url, final_endpoint_success, body_request_success)
                api_results[endpoint_key]["success_responses"].append(rs)

            # Then test with attack payloads
            for payload in payloads:
                datas_vul = make_datas_payload_vul(payload, format_api)
                final_endpoint_vul, body_request_vul = build_api_request(datas_vul, api.endpoint, format_api)
                response_vul = send_attack_request(api.api_type, base_url, final_endpoint_vul, body_request_vul)
                response_vul['api_id'] = api.api_id
                response_vul['payload'] = payload
                api_results[endpoint_key]["suspicious_responses"].append(response_vul)

        except Exception as e:
            print(f"Error processing API {api.endpoint}: {str(e)}")
            continue

    # Categorize all suspicious responses
    high_danger_all = []
    medium_danger_all = []
    low_danger_all = []

    for endpoint, results in api_results.items():
        high, medium, low = categorize_suspicious_responses(
            results["success_responses"],
            results["suspicious_responses"]
        )
        high_danger_all.extend(high)
        medium_danger_all.extend(medium)
        low_danger_all.extend(low)

    return {
        "status": "SUCCESS",
        "data": {
            "total_apis_scanned": len(apis),
            "suspicious_responses": len(high_danger_all) + len(medium_danger_all) + len(low_danger_all),
            "normal_responses": sum(len(r["success_responses"]) for r in api_results.values()),
            "high_danger_responses": high_danger_all,
            "medium_danger_responses": medium_danger_all,
            "low_danger_responses": low_danger_all
        },
        "message": "Scan completed successfully"
    }


def send_attack_request(http_method, base_url, final_endpoint, body_request):
    url = f"{base_url}{final_endpoint}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body_request) if body_request else None
    start_time = time.time()

    try:
        response = requests.request(
            method=http_method,
            url=url,
            data=data,
            headers=headers,
            timeout=10
        )
        status = response.status_code
        response_text = response.text
    except Exception as e:
        status = 500
        response_text = str(e)

    end_time = time.time()
    response_time = end_time - start_time

    request_info = {
        "method": http_method,
        "url": url,
        "headers": headers,
        "body": body_request
    }

    print(request_info)

    return {
        "request": request_info,
        "status": status,
        "response": response_text,
        "response_time": response_time
    }
