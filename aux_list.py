"""auxiliary functions on lists"""

def flatten_list(nested_list: list[list]) -> list:
    return sum(nested_list, [])

def split_at_index(data: list|tuple, index: int) -> tuple[list|tuple, list|tuple]:
    return data[:index], data[index:]

