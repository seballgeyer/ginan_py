def match_patterns(patterns, value):
    for pattern in patterns:
        if matches_pattern(pattern, value):
            return True
    return False



def matches_pattern(pattern, value):
    if "?" in pattern:
        return matches_question_mark_pattern(pattern, value)
    if "*" in pattern:
        return matches_asterisk_pattern(pattern, value)
    return pattern == value


def matches_question_mark_pattern(pattern, value):
    if len(pattern) != len(value):
        return False

    for p, v in zip(pattern, value):
        if p != "?" and p != v:
            return False

    return True


def matches_asterisk_pattern(pattern, value):
    pattern_parts = pattern.split("*")
    if len(pattern_parts) == 1 and value == pattern:
        return True
    if pattern_parts[0] == "":
        return value.endswith(pattern_parts[-1])
    if pattern_parts[-1] == "":
        return value.startswith(pattern_parts[0])
    return value.startswith(pattern_parts[0]) and value.endswith(pattern_parts[-1])
