import random
import string

from src.services.api.format_api_handler_service import get_default_values, get_element_type


def generate_simple_test_data(format_api, a, c):
    default_values = get_default_values(format_api)

    element_types = get_element_type(format_api)

    result = []

    for _ in range(c):
        sample = []
        for i, default in enumerate(default_values):
            if i == 0:
                sample.append(a)
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
