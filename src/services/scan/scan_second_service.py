import json

from src.repositories.api_repository import get_api_by_api_id
from src.repositories.vul_repository import create_vul
from src.services.payload.generate_payload_service import generate_datas_payload_success, generate_simple_test_data
from src.services.payload.payload_service import generate_payloads_child
from src.services.protect.regex_service import generate_regex_by_payloads
from src.services.scan.analysis_service import categorize_suspicious_responses
from src.services.scan.format_api_handler_service import build_api_request, get_element_count, get_element_names
from src.services.scan.scan_service import send_attack_request
from src.services.scan.validate_scan_service import validate_scan


def scan_api_2(data):
    base_url, project_id, api_payloads = validate_scan(data)

    api_results = {}
    high_risk_payloads = []

    for api_payload in api_payloads:
        api = get_api_by_api_id(api_payload["api_id"])
        format_api = json.loads(api.format_api)
        endpoint_key = f"{api.api_type}:{api.endpoint}"

        if endpoint_key not in api_results:
            api_results[endpoint_key] = {
                "success_responses": [],
                "suspicious_responses": []
            }

        try:
            success_data = generate_datas_payload_success(format_api)
            success_responses = []

            for data in success_data:
                final_endpoint_success, body_request_success = build_api_request(data, api.endpoint, format_api)
                rs = send_attack_request(api.api_type, base_url, final_endpoint_success, body_request_success)
                success_responses.append(rs)

            api_results[endpoint_key]["success_responses"] = success_responses

            high, medium, low = handler_analyst(
                api,
                base_url,
                api_payload["payload"],
                success_responses=success_responses
            )

            if isinstance(high, list) and high:
                for high_item in high:
                    if isinstance(high_item, dict):
                        element_name = get_element_names(high_item.get("format_api", {}))[
                            int(high_item.get("cnt", 0))] if high_item.get("format_api") else ""

                        high_risk_payload = {
                            "cnt": high_item.get("cnt"),
                            "api_id": high_item.get("api_id"),
                            "payload": high_item.get("payload"),
                            "element_name": element_name,
                            "endpoint": api.endpoint,
                            "api_type": api.api_type
                        }
                        high_risk_payloads.append(high_risk_payload)

                        variant_payloads = generate_payloads_child(high_item.get("payload"), 10)
                        for variant_payload in variant_payloads:
                            new_data_vul = []
                            original_data_vul = high_item.get("data_vul")

                            if isinstance(original_data_vul, list):
                                new_data_vul = original_data_vul.copy()
                                cnt_index = int(high_item.get("cnt", 0))
                                if cnt_index < len(new_data_vul):
                                    new_data_vul[cnt_index] = variant_payload
                            elif isinstance(original_data_vul, dict):
                                new_data_vul = original_data_vul.copy()
                                if element_name:
                                    new_data_vul[element_name] = variant_payload
                            else:
                                new_data_vul = generate_simple_test_data(
                                    format_api,
                                    variant_payload,
                                    get_element_count(format_api)
                                )
                                if isinstance(new_data_vul, list) and len(new_data_vul) > 0:
                                    new_data_vul = [new_data_vul[0]]

                            variant_high, variant_medium, variant_low = handler_analyst(
                                api,
                                base_url,
                                variant_payload,
                                success_responses=success_responses,
                                datas_vul=[new_data_vul] if not isinstance(new_data_vul, list) else new_data_vul
                            )

                            if variant_high:
                                high_risk_payloads.append({
                                    "cnt": high_item.get("cnt"),
                                    "api_id": api.api_id,
                                    "payload": variant_payload,
                                    "element_name": element_name,
                                    "endpoint": api.endpoint,
                                    "api_type": api.api_type,
                                    "variant_of": high_item.get("payload")
                                })

        except Exception as e:
            print(f"Error processing API {api.endpoint}: {str(e)}")
            continue

    api_payloads_list = transform_high_risk_payloads(high_risk_payloads)
    for api_payload in api_payloads_list:
        regex_obj = generate_regex_by_payloads(api_payload['payloads'])
        regex = regex_obj['regex']
        create_vul(
            api_payload['api_id'],
            api_payload['payloads'],
            regex,
            api_payload['cnt'],
        )

    return {
        "data": high_risk_payloads,
    }


def handler_analyst(api, base_url, payload, success_responses=None, datas_vul=None):
    api_results = {}
    format_api = json.loads(api.format_api)
    endpoint_key = f"{api.api_type}:{api.endpoint}"

    if endpoint_key not in api_results:
        api_results[endpoint_key] = {
            "success_responses": [],
            "suspicious_responses": []
        }

    try:
        if success_responses:
            api_results[endpoint_key]["success_responses"] = success_responses
        else:
            datas_success = generate_datas_payload_success(format_api)
            for data in datas_success:
                final_endpoint_success, body_request_success = build_api_request(data, api.endpoint, format_api)
                rs = send_attack_request(api.api_type, base_url, final_endpoint_success, body_request_success)
                api_results[endpoint_key]["success_responses"].append(rs)

        if not datas_vul:
            datas_vul = generate_simple_test_data(format_api, payload, get_element_count(format_api))

        cnt = 0
        for data_vul in datas_vul:
            final_endpoint_vul, body_request_vul = build_api_request(data_vul, api.endpoint, format_api)
            response_vul = send_attack_request(api.api_type, base_url, final_endpoint_vul, body_request_vul)
            response_vul["api_id"] = api.api_id
            response_vul["format_api"] = format_api
            response_vul["payload"] = payload
            response_vul["data_vul"] = data_vul
            response_vul["cnt"] = cnt
            api_results[endpoint_key]["suspicious_responses"].append(response_vul)
            cnt += 1

    except Exception as e:
        print(f"Error processing API {api.endpoint} in {api.api_id}: {str(e)}")

    return categorize_suspicious_responses(
        api_results[endpoint_key]["success_responses"],
        api_results[endpoint_key]["suspicious_responses"]
    )


def transform_high_risk_payloads(high_risk_payloads):
    grouped_payloads = {}

    for payload_item in high_risk_payloads:
        api_id = payload_item.get("api_id")
        payload = payload_item.get("payload")
        cnt = payload_item.get("cnt")

        if api_id and payload:
            key = f"{api_id}:{cnt}"
            if key not in grouped_payloads:
                grouped_payloads[key] = {
                    "api_id": api_id,
                    "payloads": [],
                    "cnt": cnt
                }

            if payload not in grouped_payloads[key]["payloads"]:
                grouped_payloads[key]["payloads"].append(payload)

    return list(grouped_payloads.values())
