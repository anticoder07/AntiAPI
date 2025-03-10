import difflib
import re
from itertools import combinations


def generate_regex_by_payloads(payloads):
    if not payloads:
        return {'regex': ''}

    # Nếu chỉ có 1 payload, xác định pattern dựa trên nội dung mẫu.
    if len(payloads) == 1:
        sample = payloads[0]
        if '{{' in sample and '}}' in sample:
            regex = r'{{(.*?)}}'
        elif '<' in sample and '>' in sample:
            regex = r'<(.*?)>'
        else:
            regex = r'([^\w\s]+.*?[^\w\s]+)'
    else:
        common_patterns = find_common_patterns_with_difflib(payloads)
        if common_patterns:
            common_patterns.sort(key=len, reverse=True)
            best_pattern = common_patterns[0]
            if len(best_pattern) >= 2:
                positions = [p.find(best_pattern) for p in payloads if best_pattern in p]
                if positions and all(pos >= 0 for pos in positions):
                    avg_pos = sum(positions) / len(positions)
                    # Nếu pattern nằm gần đầu
                    if avg_pos < len(best_pattern):
                        escaped_pattern = re.escape(best_pattern)
                        regex = f"{escaped_pattern}(.*)"
                    # Nếu pattern nằm gần cuối
                    elif avg_pos > (len(payloads[0]) - len(best_pattern) - 5):
                        escaped_pattern = re.escape(best_pattern)
                        regex = f"(.*){escaped_pattern}"
                    else:
                        left_parts = set()
                        right_parts = set()
                        for payload in payloads:
                            if best_pattern in payload:
                                idx = payload.find(best_pattern)
                                left = payload[:idx]
                                right = payload[idx + len(best_pattern):]
                                if left:
                                    left_parts.add(left)
                                if right:
                                    right_parts.add(right)
                        if len(left_parts) == 1 and len(right_parts) == 1:
                            left_pattern = re.escape(list(left_parts)[0])
                            right_pattern = re.escape(list(right_parts)[0])
                            regex = f"{left_pattern}(.*?){right_pattern}"
                        else:
                            escaped_pattern = re.escape(best_pattern)
                            regex = f"(.*?){escaped_pattern}(.*?)"
                else:
                    regex = determine_delimiter_pattern(payloads)
            else:
                regex = determine_delimiter_pattern(payloads)
        else:
            regex = determine_delimiter_pattern(payloads)

    return {'regex': regex}


def find_common_patterns_with_difflib(payloads):
    common_patterns = []
    for payload1, payload2 in combinations(payloads, 2):
        matcher = difflib.SequenceMatcher(None, payload1, payload2)
        matching_blocks = matcher.get_matching_blocks()
        for match in matching_blocks:
            i, j, size = match
            if size > 1:
                common_pattern = payload1[i:i + size]
                if common_pattern.strip() and common_pattern not in common_patterns:
                    common_patterns.append(common_pattern)
    return common_patterns


def determine_delimiter_pattern(payloads):
    has_curly_braces = all('{{' in p and '}}' in p for p in payloads)
    has_angle_brackets = all('<' in p and '>' in p for p in payloads)

    if has_curly_braces:
        return r'{{(.*?)}}'
    elif has_angle_brackets:
        return r'<(.*?)>'
    else:
        delimiters = [('(', ')'), ('[', ']'), ('/*', '*/'), ('${', '}'), ('`', '`'), ("'", "'"), ('"', '"')]
        for left, right in delimiters:
            if all(left in p and right in p for p in payloads):
                escaped_left = re.escape(left)
                escaped_right = re.escape(right)
                return f"{escaped_left}(.*?){escaped_right}"
        return r'([^\w\s]+.*?[^\w\s]+)'


def validate_requests(request_content, regex):
    match = re.search(regex, request_content)
    return match is None


def filter_requests(request_content, regex):
    matches = re.findall(regex, request_content)
    if matches and isinstance(matches[0], tuple):
        matches = [match[0] for match in matches]
    return [match.strip() for match in matches if match and match.strip()]
