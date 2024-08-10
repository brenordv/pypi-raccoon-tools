from typing import List, Any, Generator


def infinite_iterator(list_to_iterate_over: List[Any]) -> Generator[Any, None, None]:
    """
    Generate an infinite iterator from a list.
    """
    while True:
        for item in list_to_iterate_over:
            yield item


if __name__ == '__main__':
    # Example usage of infinite_iterator
    infinite_iter = infinite_iterator([1, 2, 3])
    for i, item_from_list in enumerate(infinite_iter):
        print(f"Item {i + 1}: {item_from_list}")
        if i > 10:
            break
