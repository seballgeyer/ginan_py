from typing import List

def find_common(a, b):
    a_dict = {tuple(item.id.items()): i for i, item in enumerate(a)}
    b_dict = {tuple(item.id.items()): i for i, item in enumerate(b)}

    common = []
    non_common_a = []
    non_common_b = []

    for i, item in enumerate(b):
        if tuple(item.id.items()) in a_dict:
            common.append((a_dict[tuple(item.id.items())], i))
        else:
            non_common_b.append(i)

    for i, item in enumerate(a):
        if tuple(item.id.items()) not in b_dict:
            non_common_a.append(i)

    return common, non_common_a, non_common_b

def compare_dict(dict1: dict, dict2:dict, comparison_keys:List = None) -> bool:
    """
    Compare two dictionaries on the set of common keys, or keys provided in the comparison_keys list.
        return True if they are equal, False otherwise.
    """
    if comparison_keys is None:
        comparison_keys = set(dict1.keys()).intersection(set(dict2.keys()))
    print(comparison_keys)
    return all(key in dict1 and key in dict2 and dict1[key] == dict2[key] for key in comparison_keys)