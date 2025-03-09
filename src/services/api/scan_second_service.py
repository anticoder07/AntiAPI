import json
from http import HTTPStatus

from flask import g

from src.commons.exception.custom_exception.custom_exception import CustomException
from src.repositories.api_repository import get_api_by_api_id
from src.repositories.project_repository import get_project_by_project_id
from src.services.analysis_service import categorize_suspicious_responses
from src.services.api.format_api_handler_service import build_api_request, get_element_count, get_element_names
from src.services.api.scan_service import send_attack_request
from src.services.api.scan_success_service import make_datas_payload_success
from src.services.api.sinh_payload import generate_variants
from src.services.api.temp import generate_simple_test_data


def scan_api_2(data):
    base_url = data.get("base_url")
    project_id = data.get("project_id")
    api_payloads = data.get("api_payload")

    # Phần kiểm tra tham số vẫn giữ nguyên
    if base_url is None:
        raise CustomException("base_url cannot be None", HTTPStatus.BAD_REQUEST)
    if project_id is None:
        raise CustomException("project_id cannot be None", HTTPStatus.BAD_REQUEST)

    project = get_project_by_project_id(project_id)
    if project is None or str(project.company_id) != str(g.company_id):
        raise CustomException("project_id is invalid or not accessible", HTTPStatus.BAD_REQUEST)

    api_results = {}
    high_danger_all = []

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
            # Tạo và cache success_responses cho API này
            success_data = make_datas_payload_success(format_api)
            success_responses = []

            for data in success_data:
                final_endpoint_success, body_request_success = build_api_request(data, api.endpoint, format_api)
                rs = send_attack_request(api.api_type, base_url, final_endpoint_success, body_request_success)
                success_responses.append(rs)

            # Lưu các success_responses để tái sử dụng
            api_results[endpoint_key]["success_responses"] = success_responses

            # Sử dụng hàm handler_analyst với success_responses đã có
            high, medium, low = handler_analyst(
                api,
                base_url,
                api_payload["payload"],
                success_responses=success_responses
            )

            # Xử lý kết quả high như trước đây
            if isinstance(high, list) and high:
                first_high = high[0]
                if isinstance(first_high, dict):
                    high_info = {
                        "api_id": first_high.get("api_id"),
                        "payload": first_high.get("payload"),
                        "data_vul": first_high.get("data_vul"),
                        "cnt": first_high.get("cnt"),
                        "element_name": get_element_names(first_high.get("format_api", {}))[
                            int(first_high.get("cnt", 0))]
                    }
                    high_danger_all.append(high_info)

                    # Tạo các biến thể payload và test lại ngay
                    variant_payloads = generate_variants(high_info["payload"], 10)

                    # Tạo dữ liệu test mới cho các payload biến thể
                    variant_results = []
                    for variant_payload in variant_payloads:
                        # Tạo data_vul mới với payload biến thể
                        new_data_vul = []
                        original_data_vul = high_info["data_vul"]

                        # Cập nhật payload trong data_vul
                        if isinstance(original_data_vul, list):
                            new_data_vul = original_data_vul.copy()
                            cnt_index = int(high_info["cnt"])
                            if cnt_index < len(new_data_vul):
                                new_data_vul[cnt_index] = variant_payload
                        elif isinstance(original_data_vul, dict):
                            new_data_vul = original_data_vul.copy()
                            element_name = high_info["element_name"]
                            new_data_vul[element_name] = variant_payload
                        else:
                            # Tạo data_vul mới nếu định dạng không rõ ràng
                            new_data_vul = generate_simple_test_data(
                                format_api,
                                variant_payload,
                                get_element_count(format_api)
                            )
                            if isinstance(new_data_vul, list) and len(new_data_vul) > 0:
                                new_data_vul = [new_data_vul[0]]  # Chỉ lấy phần tử đầu tiên để tối ưu

                        # Test với payload biến thể và TÁI SỬ DỤNG success_responses đã có
                        variant_high, variant_medium, variant_low = handler_analyst(
                            api,
                            base_url,
                            variant_payload,
                            success_responses=success_responses,  # Tái sử dụng success_responses
                            datas_vul=[new_data_vul] if not isinstance(new_data_vul, list) else new_data_vul
                        )

                        # Lưu kết quả
                        if variant_high:
                            variant_results.append({
                                "variant_payload": variant_payload,
                                "result": "high"
                            })
                        elif variant_medium:
                            variant_results.append({
                                "variant_payload": variant_payload,
                                "result": "medium"
                            })
                        elif variant_low:
                            variant_results.append({
                                "variant_payload": variant_payload,
                                "result": "low"
                            })
                        else:
                            variant_results.append({
                                "variant_payload": variant_payload,
                                "result": "none"
                            })

                    # Thêm kết quả từ các biến thể vào high_info
                    high_info["variant_results"] = variant_results

        except Exception as e:
            print(f"Error processing API {api.endpoint}: {str(e)}")
            continue

    return {
        "status": "SUCCESS",
        "data": {
            "high_danger_all": high_danger_all
        },
        "message": "Scan completed successfully"
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
        # Sử dụng success_responses từ tham số nếu có, nếu không thì tạo mới
        if success_responses:
            api_results[endpoint_key]["success_responses"] = success_responses
        else:
            datas_success = make_datas_payload_success(format_api)
            for data in datas_success:
                final_endpoint_success, body_request_success = build_api_request(data, api.endpoint, format_api)
                rs = send_attack_request(api.api_type, base_url, final_endpoint_success, body_request_success)
                api_results[endpoint_key]["success_responses"].append(rs)

        # Sử dụng datas_vul từ tham số nếu có, nếu không thì tạo mới
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
        print(f"Error processing API {api.endpoint}: {str(e)}")
        # Không dùng continue vì không nằm trong vòng lặp

    # Trả về kết quả phân loại các phản hồi đáng ngờ
    return categorize_suspicious_responses(
        api_results[endpoint_key]["success_responses"],
        api_results[endpoint_key]["suspicious_responses"]
    )
# import json
# from http import HTTPStatus
#
# from flask import g
#
# from src.commons.exception.custom_exception.custom_exception import CustomException
# from src.repositories.api_repository import get_api_by_api_id
# from src.repositories.project_repository import get_project_by_project_id
# from src.services.analysis_service import categorize_suspicious_responses
# from src.services.api.format_api_handler_service import build_api_request, get_element_count, get_element_names
# from src.services.api.scan_service import send_attack_request
# from src.services.api.scan_success_service import make_datas_payload_success
# from src.services.api.sinh_payload import generate_variants
# from src.services.api.temp import generate_simple_test_data
#
#
# def scan_api_2(data):
#     base_url = data.get("base_url")
#     project_id = data.get("project_id")
#     api_payloads = data.get("api_payload")
#
#     # Phần kiểm tra tham số vẫn giữ nguyên
#     if base_url is None:
#         raise CustomException("base_url cannot be None", HTTPStatus.BAD_REQUEST)
#     if project_id is None:
#         raise CustomException("project_id cannot be None", HTTPStatus.BAD_REQUEST)
#
#     project = get_project_by_project_id(project_id)
#     if project is None or str(project.company_id) != str(g.company_id):
#         raise CustomException("project_id is invalid or not accessible", HTTPStatus.BAD_REQUEST)
#
#     api_results = {}
#     high_danger_all = []
#
#     for api_payload in api_payloads:
#         api = get_api_by_api_id(api_payload["api_id"])
#         format_api = json.loads(api.format_api)
#         endpoint_key = f"{api.api_type}:{api.endpoint}"
#
#         if endpoint_key not in api_results:
#             api_results[endpoint_key] = {
#                 "success_responses": [],
#                 "suspicious_responses": []
#             }
#
#         try:
#             # Sử dụng hàm handler_analyst đã tạo
#             high, medium, low = handler_analyst(api, base_url, api_payload["payload"])
#
#             # Xử lý kết quả high như trước đây
#             if isinstance(high, list) and high:
#                 first_high = high[0]
#                 if isinstance(first_high, dict):
#                     high_info = {
#                         "api_id": first_high.get("api_id"),
#                         "payload": first_high.get("payload"),
#                         "data_vul": first_high.get("data_vul"),
#                         "cnt": first_high.get("cnt"),
#                         "element_name": get_element_names(first_high.get("format_api", {}))[
#                             int(first_high.get("cnt", 0))]
#                     }
#                     high_danger_all.append(high_info)
#
#                     # Tạo các biến thể payload và test lại ngay
#                     variant_payloads = generate_variants(high_info["payload"], 10)
#
#                     # Tạo dữ liệu test mới cho các payload biến thể
#                     variant_results = []
#                     for variant_payload in variant_payloads:
#                         # Tạo data_vul mới với payload biến thể
#                         # Chỉ thay thế payload ở vị trí đã xác định là có lỗi (cnt)
#                         new_data_vul = high_info[
#                             "data_vul"].copy()  # Giả định data_vul là một list hoặc dict có thể copy
#
#                         # Cần xử lý tùy thuộc vào cấu trúc của data_vul
#                         # Đây là ví dụ, bạn cần điều chỉnh dựa trên cấu trúc thực tế của data_vul
#                         if isinstance(new_data_vul, list):
#                             new_data_vul[int(high_info["cnt"])] = variant_payload
#                         elif isinstance(new_data_vul, dict):
#                             element_name = high_info["element_name"]
#                             new_data_vul[element_name] = variant_payload
#
#                         # Test với payload biến thể
#                         variant_high, variant_medium, variant_low = handler_analyst(
#                             api,
#                             base_url,
#                             variant_payload,
#                             datas_vul=[new_data_vul]  # Chỉ test với data_vul mới, không cần sinh lại
#                         )
#
#                         # Lưu kết quả
#                         if variant_high:
#                             variant_results.append({
#                                 "variant_payload": variant_payload,
#                                 "result": "high"
#                             })
#                         elif variant_medium:
#                             variant_results.append({
#                                 "variant_payload": variant_payload,
#                                 "result": "medium"
#                             })
#                         elif variant_low:
#                             variant_results.append({
#                                 "variant_payload": variant_payload,
#                                 "result": "low"
#                             })
#
#                     # Thêm kết quả từ các biến thể vào high_info
#                     high_info["variant_results"] = variant_results
#
#         except Exception as e:
#             print(f"Error processing API {api.endpoint}: {str(e)}")
#             continue
#
#     return {
#         "status": "SUCCESS",
#         "data": {
#             "high_danger_all": high_danger_all
#         },
#         "message": "Scan completed successfully"
#     }
#
# def handler_analyst(api, base_url, payload, datas_success=None, datas_vul=None):
#     api_results = {}
#     format_api = json.loads(api.format_api)
#     endpoint_key = f"{api.api_type}:{api.endpoint}"
#
#     if endpoint_key not in api_results:
#         api_results[endpoint_key] = {
#             "success_responses": [],
#             "suspicious_responses": []
#         }
#
#     try:
#         # Sử dụng datas_success từ tham số nếu có, nếu không thì tạo mới
#         if not datas_success:
#             datas_success = make_datas_payload_success(format_api)
#
#         for data in datas_success:
#             final_endpoint_success, body_request_success = build_api_request(data, api.endpoint, format_api)
#             rs = send_attack_request(api.api_type, base_url, final_endpoint_success, body_request_success)
#             api_results[endpoint_key]["success_responses"].append(rs)
#
#         # Sử dụng datas_vul từ tham số nếu có, nếu không thì tạo mới
#         if not datas_vul:
#             datas_vul = generate_simple_test_data(format_api, payload, get_element_count(format_api))
#
#         cnt = 0
#         for data_vul in datas_vul:
#             final_endpoint_vul, body_request_vul = build_api_request(data_vul, api.endpoint, format_api)
#             response_vul = send_attack_request(api.api_type, base_url, final_endpoint_vul, body_request_vul)
#             response_vul["api_id"] = api.api_id
#             response_vul["format_api"] = format_api
#             response_vul["payload"] = payload
#             response_vul["data_vul"] = data_vul
#             response_vul["cnt"] = cnt
#             api_results[endpoint_key]["suspicious_responses"].append(response_vul)
#             cnt += 1
#
#     except Exception as e:
#         print(f"Error processing API {api.endpoint}: {str(e)}")
#         # Không dùng continue vì không nằm trong vòng lặp
#
#     # Trả về kết quả phân loại các phản hồi đáng ngờ
#     return categorize_suspicious_responses(
#         api_results[endpoint_key]["success_responses"],
#         api_results[endpoint_key]["suspicious_responses"]
#     )

#
# def scan_api_2(data):
#     base_url = data.get("base_url")
#     project_id = data.get("project_id")
#     api_payloads = data.get("api_payload")
#
#     if base_url is None:
#         raise CustomException("base_url cannot be None", HTTPStatus.BAD_REQUEST)
#     if project_id is None:
#         raise CustomException("project_id cannot be None", HTTPStatus.BAD_REQUEST)
#
#     project = get_project_by_project_id(project_id)
#     if project is None or str(project.company_id) != str(g.company_id):
#         raise CustomException("project_id is invalid or not accessible", HTTPStatus.BAD_REQUEST)
#
#     api_results = {}
#
#     for api_payload in api_payloads:
#         api = get_api_by_api_id(api_payload["api_id"])
#         format_api = json.loads(api.format_api)
#         endpoint_key = f"{api.api_type}:{api.endpoint}"
#
#         if endpoint_key not in api_results:
#             api_results[endpoint_key] = {
#                 "success_responses": [],
#                 "suspicious_responses": []
#             }
#
#         try:
#             datas_success = make_datas_payload_success(format_api)
#             for data in datas_success:
#                 final_endpoint_success, body_request_success = build_api_request(data, api.endpoint, format_api)
#                 rs = send_attack_request(api.api_type, base_url, final_endpoint_success, body_request_success)
#                 api_results[endpoint_key]["success_responses"].append(rs)
#
#             datas_vul_list = generate_simple_test_data(format_api, api_payload["payload"],
#                                                        get_element_count(format_api))
#             cnt = 0
#             for data_vul in datas_vul_list:
#                 final_endpoint_vul, body_request_vul = build_api_request(data_vul, api.endpoint, format_api)
#                 response_vul = send_attack_request(api.api_type, base_url, final_endpoint_vul, body_request_vul)
#                 response_vul["api_id"] = api.api_id
#                 response_vul["format_api"] = format_api
#                 response_vul["payload"] = api_payload["payload"]
#                 response_vul["data_vul"] = data_vul
#                 response_vul["cnt"] = cnt
#                 api_results[endpoint_key]["suspicious_responses"].append(response_vul)
#                 cnt += 1
#
#         except Exception as e:
#             print(f"Error processing API {api.endpoint}: {str(e)}")
#             continue
#
#     high_danger_all = []
#
#     for endpoint, results in api_results.items():
#         high, medium, low = categorize_suspicious_responses(
#             results["success_responses"],
#             results["suspicious_responses"]
#         )
#
#         # Kiểm tra nếu high không rỗng và là list
#         if isinstance(high, list) and high:
#             first_high = high[0]  # Lấy phần tử đầu tiên nếu có nhiều
#             if isinstance(first_high, dict):  # Kiểm tra nếu first_high là dictionary
#                 high_danger_all.append({
#                     "api_id": first_high.get("api_id"),
#                     "payload": first_high.get("payload"),
#                     "data_vul": first_high.get("data_vul"),
#                     "cnt": first_high.get("cnt"),
#                     "element_name": get_element_names(first_high.get("format_api", {}))[int(first_high.get("cnt", 0))]
#                 })
#
#     for h in high_danger_all:
#         plc = generate_variants(h["payload"], 10)
#
#     return {
#         "status": "SUCCESS",
#         "data": {
#             "high_danger_all": high_danger_all
#         },
#         "message": "Scan completed successfully"
#     }
