char_groups = {
    "operators": ["+", "-", "*", "/", "%", "×", "·", "**"],
    "brackets": ["{}", "[]", "()", "<>", "%%", "[%]", "(( ))", "{% %}"],
    "quotes": ['"', "'", "`", "“”", "‘’"],
    "whitespace": [" ", "\t", "\n", "%20"],
    "delimiters": [";", ",", ".", ":"],
    "numbers": [str(i) for i in range(10)]
}


def generate_variants(payload, limit=None):
    variants = set([payload])

    for key, group in char_groups.items():
        for char in group:
            if any(c in payload for c in group):
                for replacement in group:
                    new_payload = payload
                    for c in group:
                        new_payload = new_payload.replace(c, replacement)
                    variants.add(new_payload)

                    if limit and len(variants) >= limit:
                        return list(variants)

    return list(variants)[:limit] if limit else list(variants)
