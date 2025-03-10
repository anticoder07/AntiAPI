import difflib
import re
from collections import Counter


def is_suspicious_response(success_responses, suspicious_response):
    if not success_responses or not suspicious_response:
        return False, {"reason": "No comparison data available"}

    suspicious_url = suspicious_response['request']['url']
    suspicious_method = suspicious_response['request']['method']

    base_url = suspicious_url.split('?')[0]
    matching_responses = [
        response for response in success_responses
        if response['request']['url'].split('?')[0] == base_url and
           response['request']['method'] == suspicious_method
    ]

    if not matching_responses:
        return True, {"reason": "No matching endpoint found in success responses"}

    common_status = most_common_value([r['status'] for r in matching_responses])
    response_bodies = [r['response'] for r in matching_responses if r['response']]

    avg_response_time = sum(r['response_time'] for r in matching_responses) / len(matching_responses)

    suspicious_body = suspicious_response['response'] if suspicious_response['response'] else ""

    suspicious_keywords = [
        "error", "exception", "warning", "fail", "denied", "invalid",
        "hack", "root:", "SELECT", "syntax", "command", "injection",
        "shell", "admin", "password", "credentials", "/etc/", "tmp",
        "unauthorized", "forbidden", "attack"
    ]

    error_patterns = [
        r"error\s+\d+", r"exception", r"stack\s+trace", r"warning",
        r"[A-Za-z\.]+Exception", r"fail", r"denied", r"invalid",
        r"syntax\s+error", r"command\s+not\s+found"
    ]

    if suspicious_response['status'] != common_status:
        return True, {"reason": f"Status code differs: expected {common_status}, got {suspicious_response['status']}"}

    has_body_normally = any(body for body in response_bodies)
    if has_body_normally and not suspicious_body:
        return True, {"reason": "Missing response body when one was expected"}

    if not has_body_normally and suspicious_body:
        return True, {"reason": "Unexpected response body"}

    if not has_body_normally and not suspicious_body:
        return False, {"reason": "No response bodies to compare"}

    highest_similarity = 0
    for base_body in response_bodies:
        matcher = difflib.SequenceMatcher(None, base_body, suspicious_body)
        similarity = matcher.ratio()
        highest_similarity = max(highest_similarity, similarity)

    if highest_similarity < 0.85:
        return True, {
            "reason": f"Response differs significantly from normal responses (similarity: {highest_similarity:.2f})"
        }

    for keyword in suspicious_keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in suspicious_body.lower() and not any(
                keyword_lower in body.lower() for body in response_bodies):
            return True, {"reason": f"Suspicious keyword found: {keyword}"}

    for pattern in error_patterns:
        suspicious_matches = re.findall(pattern, suspicious_body, re.IGNORECASE)
        if suspicious_matches and not any(re.findall(pattern, body, re.IGNORECASE) for body in response_bodies):
            return True, {"reason": f"Suspicious pattern found: {pattern}"}

    avg_size = sum(len(body) for body in response_bodies) / len(response_bodies)
    size_ratio = min(len(suspicious_body), avg_size) / max(len(suspicious_body), avg_size)
    if size_ratio < 0.75:
        return True, {"reason": f"Response size differs significantly: {len(suspicious_body)} vs avg {avg_size:.0f}"}

    if (suspicious_response['response_time'] > avg_response_time * 3 and
            suspicious_response['response_time'] > 2):
        return True, {
            "reason": f"Response time unusually high: {suspicious_response['response_time']:.2f}s vs avg {avg_response_time:.2f}s"
        }

    return False, {"reason": "Response appears normal"}


def most_common_value(values):
    if not values:
        return None

    count = Counter(values)
    return count.most_common(1)[0][0]


def categorize_suspicious_responses(success_responses, suspicious_responses):
    high_danger = []
    medium_danger = []
    low_danger = []

    # Command injection patterns (high risk)
    command_injection_patterns = [
        r"([;|&]|\|\||\`|\/bin\/)",
        r"cat\s+\/etc",
        r"whoami",
        r"reboot",
        r"rm\s+-rf",
        r"echo\s+.*hacked"
    ]

    # SQL injection patterns (medium-high risk)
    sql_injection_patterns = [
        r"SELECT.*FROM",
        r"UNION.*SELECT",
        r"--.*",
        r"'.*OR.*'.*='",
        r"1=1",
        r"DROP.*TABLE"
    ]

    for response in suspicious_responses:
        is_suspicious, details = is_suspicious_response(success_responses, response)

        if not is_suspicious:
            response['danger_level'] = "low"
            response['reason'] = details.get("reason", "Minor anomaly detected")
            low_danger.append(response)
            continue

        url = response['request']['url']
        body = response['response'] if response['response'] else ""

        high_danger_match = False
        for pattern in command_injection_patterns:
            if re.search(pattern, url, re.IGNORECASE) or re.search(pattern, body, re.IGNORECASE):
                high_danger_match = True
                break

        if high_danger_match or "echo hacked" in body or "hacked" in body:
            response['danger_level'] = "high"
            response['reason'] = details.get("reason", "Command injection detected")
            high_danger.append(response)
            continue

        medium_danger_match = False
        for pattern in sql_injection_patterns:
            if re.search(pattern, url, re.IGNORECASE) or re.search(pattern, body, re.IGNORECASE):
                medium_danger_match = True
                break

        if medium_danger_match or "denied" in body or "unauthorized" in body:
            response['danger_level'] = "medium"
            response['reason'] = details.get("reason", "Possible SQL injection or access attempt")
            medium_danger.append(response)
            continue

        response['danger_level'] = "low"
        response['reason'] = details.get("reason", "Minor anomaly detected")
        low_danger.append(response)

    return high_danger, medium_danger, low_danger
