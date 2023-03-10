def match_patterns(patterns, value):
    for pattern in patterns:
        if not is_valid_pattern(pattern):
            raise ValueError(f"Invalid pattern: {pattern}")

        if matches_pattern(pattern, value):
            return True

    return False


def is_valid_pattern(pattern):
    if pattern.count("*") > 1 or ("?" in pattern and pattern.count("?") != 1):
        return False
    return True


def matches_pattern(pattern, value):
    if "?" in pattern:
        return matches_question_mark_pattern(pattern, value)
    if "*" in pattern:
        return matches_asterisk_pattern(pattern, value)
    return pattern == value


def matches_question_mark_pattern(pattern, value):
    if len(value) == len(pattern) and all(v == p or p == "?" for v, p in zip(value, pattern)):
        return True
    return False


def matches_asterisk_pattern(pattern, value):
    pattern_parts = pattern.split("*")
    if len(pattern_parts) == 1 and value == pattern:
        return True
    if pattern_parts[0] == "":
        return value.endswith(pattern_parts[-1])
    if pattern_parts[-1] == "":
        return value.startswith(pattern_parts[0])
    return value.startswith(pattern_parts[0]) and value.endswith(pattern_parts[-1])
