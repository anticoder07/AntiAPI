def generate_success_payloads():
    payload_list_success_string = [
        "validInput",
        "test123",
        "safe_string",
        "hello_world",
        "abcDEF",
        "simple_text",
        "json_value",
        "payload_test",
        "user_input",
        "valid_data"
    ]

    payload_list_success_number = [
        0,
        1,
        42,
        100,
        999,
        -10,
        3.14,
        2500,
        123456,
        -99999
    ]

    return payload_list_success_string, payload_list_success_number