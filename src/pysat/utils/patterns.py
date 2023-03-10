def match_patterns(patterns, value):
    for pattern in patterns:
        # Check if the pattern is valid
        if pattern.count("*") > 1 or ("?" in pattern and pattern.count("?") != 1):
            raise ValueError(f"Invalid pattern: {pattern}")

        # Check if the value matches the pattern
        if "?" in pattern:
            if len(value) == len(pattern) and all(v == p or p == "?" for v, p in zip(value, pattern)):
                return True
        elif "*" in pattern:
            pattern_parts = pattern.split("*")
            if len(pattern_parts) == 1 and value == pattern:
                return True
            elif pattern_parts[0] == "":
                if value.endswith(pattern_parts[-1]):
                    return True
            elif pattern_parts[-1] == "":
                if value.startswith(pattern_parts[0]):
                    return True
            else:
                if value.startswith(pattern_parts[0]) and value.endswith(pattern_parts[-1]):
                    return True
        else:
            if pattern == value:
                return True
    return False
