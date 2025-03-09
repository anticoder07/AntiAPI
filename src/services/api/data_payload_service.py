import itertools
import random
import string

from src.services.api.format_api_handler_service import get_element_count, get_default_values, get_element_type


def generate_datas_payload_vul(payload, format_api):
    count = get_element_count(format_api)

    datas = []
    for i in range(count):
        datas.append(payload)

    return datas


def generate_simple_test_data(format_api, payload, limit):
    default_values = get_default_values(format_api)
    element_types = get_element_type(format_api)

    result = []

    for _ in range(limit):
        sample = []
        for i, default in enumerate(default_values):
            if i == 0:
                sample.append(payload)
            elif default is None:
                element_type = element_types[i]
                if element_type.lower() == "string":
                    sample.append(''.join(random.choices(string.ascii_lowercase, k=4)))
                elif element_type.lower() == "number":
                    sample.append(random.randint(1, 10))
                elif element_type.lower() == "array":
                    sample.append([random.randint(1, 10) for _ in range(2)])
                else:
                    sample.append(''.join(random.choices(string.ascii_lowercase, k=4)))
            elif isinstance(default, list) and len(default) > 0:
                sample.append(default[0])
            else:
                sample.append(None)

        result.append(sample)

    return result

def make_datas_payload_success(format_api):
    count = get_element_count(format_api)
    datas_default = get_default_values(format_api)
    datas_type = get_element_type(format_api)

    possible_values = []

    for i in range(count):
        if i < len(datas_default) and datas_default[i] is not None:
            element_type = datas_type[i].lower() if i < len(datas_type) and isinstance(datas_type[i],
                                                                                       str) else "unknown"

            if isinstance(datas_default[i], list) and "string" in element_type:
                extracted_values = []
                for value in datas_default[i]:
                    extracted_values.append(value)
                possible_values.append(extracted_values)
            else:
                possible_values.append([datas_default[i]])
        else:
            element_type = datas_type[i] if i < len(datas_type) else "Unknown"

            if isinstance(element_type, str):
                element_type = element_type.lower()

            if "string" in element_type:
                random_values = [
                    ''.join(random.choices(string.ascii_letters, k=5)),
                    ''.join(random.choices(string.ascii_letters, k=7))
                ]
                possible_values.append(random_values)
            elif "number" in element_type or "int" in element_type:
                random_values = [
                    random.randint(1, 100),
                    random.randint(101, 200)
                ]
                possible_values.append(random_values)
            elif "array" in element_type:
                item_type = element_type.split("<")[1].split(">")[0].lower() if "<" in element_type else "string"

                if "string" in item_type:
                    random_values = [
                        [''.join(random.choices(string.ascii_letters, k=5))],
                        [''.join(random.choices(string.ascii_letters, k=4)),
                         ''.join(random.choices(string.ascii_letters, k=6))]
                    ]
                else:
                    random_values = [
                        [random.randint(1, 50)],
                        [random.randint(51, 100), random.randint(101, 150)]
                    ]
                possible_values.append(random_values)
            else:
                random_values = [
                    ''.join(random.choices(string.ascii_letters, k=5)),
                    ''.join(random.choices(string.ascii_letters, k=7))
                ]
                possible_values.append(random_values)

    datas_list = []

    indices = [list(range(len(vals))) for vals in possible_values]
    for indices_combo in itertools.product(*indices):
        datas = [possible_values[i][idx] for i, idx in enumerate(indices_combo)]
        datas_list.append(datas)

    while len(datas_list) < 10:
        new_data = []
        for i in range(count):
            element_type = datas_type[i] if i < len(datas_type) else "Unknown"

            if isinstance(element_type, str):
                element_type = element_type.lower()

            if "string" in element_type:
                new_data.append(''.join(random.choices(string.ascii_letters, k=random.randint(5, 10))))
            elif "number" in element_type or "int" in element_type:
                new_data.append(random.randint(1, 500))
            elif "array" in element_type:
                item_type = element_type.split("<")[1].split(">")[0].lower() if "<" in element_type else "string"

                if "string" in item_type:
                    array_length = random.randint(1, 3)
                    new_data.append([
                        ''.join(random.choices(string.ascii_letters, k=random.randint(4, 8)))
                        for _ in range(array_length)
                    ])
                else:
                    array_length = random.randint(1, 3)
                    new_data.append([random.randint(1, 200) for _ in range(array_length)])
            else:
                new_data.append(''.join(random.choices(string.ascii_letters, k=random.randint(5, 10))))

        datas_list.append(new_data)

    return datas_list
