def find_common(a, b):
    a_dict = {tuple(item.measurement_id.items()): i for i, item in enumerate(a)}
    b_dict = {tuple(item.measurement_id.items()): i for i, item in enumerate(b)}

    common = []
    non_common_a = []
    non_common_b = []

    for i, item in enumerate(b):
        if tuple(item.measurement_id.items()) in a_dict:
            common.append((a_dict[tuple(item.measurement_id.items())], i))
        else:
            non_common_b.append(i)

    for i, item in enumerate(a):
        if tuple(item.measurement_id.items()) not in b_dict:
            non_common_a.append(i)

    return common, non_common_a, non_common_b
