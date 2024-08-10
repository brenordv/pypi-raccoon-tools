import time
import uuid
from typing import Generator, Callable, Optional
import random


def id_guid_generator(ids_to_generate: Optional[int] = None) -> Generator[str, None, None]:
    """
    Generate unique GUID (Globally Unique Identifier) strings.

    Args:
        ids_to_generate (Optional[int]): The number of GUIDs to generate. If None, generates indefinitely.

    Yields:
        str: A unique GUID string.

    Example:
        >>> guid_generator = id_guid_generator(5)
        >>> list(guid_generator)
        ['1234abcd-5678-90ef-ghij-klmnopqrstuv', ...]
    """
    ids_generated = 0
    while ids_to_generate is None or ids_generated < ids_to_generate:
        yield str(uuid.uuid4())
        ids_generated += 1


def id_int_generator(
    ids_to_generate: Optional[int] = None,
    start_at: int = 0,
    validate_id: Optional[Callable[[int], bool]] = None
) -> Generator[int, None, None]:
    """
    Generate integer IDs with optional validation.

    Args:
        ids_to_generate (Optional[int]): The number of IDs to generate. If None, generates indefinitely.
        start_at (int): The starting value for the ID sequence. Default is 0.
        validate_id (Optional[Callable[[int], bool]]): A function to validate each ID. If None, all IDs are considered
        valid.

    Yields:
        int: A valid integer ID.

    Example:
        >>> int_generator = id_int_generator(5, start_at=100, validate_id=lambda x: x % 2 == 0)
        >>> list(int_generator)
        [100, 102, 104, 106, 108]
    """
    ids_generated = 0
    current_id = None
    while ids_to_generate is None or ids_generated < ids_to_generate:
        current_id = start_at if current_id is None else current_id + 1

        if validate_id is not None and not validate_id(current_id):
            continue

        yield current_id
        ids_generated += 1


def timestamp_generator(timestamps_to_generate: Optional[int] = None) -> Generator[int, None, None]:
    """
    Generate Unix timestamps.

    Args:
        timestamps_to_generate (Optional[int]): The number of timestamps to generate. If None, generates indefinitely.

    Yields:
        int: A Unix timestamp (seconds since epoch).

    Example:
        >>> ts_generator = timestamp_generator(3)
        >>> list(ts_generator)
        [1628523600, 1628523601, 1628523602]
    """
    timestamps_generated = 0

    while timestamps_to_generate is None or timestamps_generated < timestamps_to_generate:
        yield int(time.time())
        timestamps_generated += 1


def sentence_generator(sentences_to_generate: Optional[int] = None,
                       min_length: int = 1,
                       max_length: Optional[int] = None) -> Generator[str, None, None]:
    """
    Generate Lorem Ipsum sentences with lengths ranging from min_length to max_length.

    Args:
        sentences_to_generate (Optional[int]): The number of sentences to generate. If None, generates indefinitely.
        min_length (int): The minimum length of each sentence. Default is 1.
        max_length (Optional[int]): The maximum length of each sentence.
                                    If None, a random value between 10 and 512 is used for each sentence.

    Yields:
        str: A Lorem Ipsum sentence.

    Example:
        >>> lorem_gen = sentence_generator(3, min_length=20, max_length=50)
        >>> list(lorem_gen)
        ['Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
         'Nullam eget felis eget nunc lobortis mattis aliquam faucibus.',
         'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.']
    """
    sentences_generated = 0

    # Lorem Ipsum text
    lorem_ipsum = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. 
    Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. 
    Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. 
    Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. 
    Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? 
    Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?
    """

    # Clean up the text and split into words
    words = lorem_ipsum.replace("\n", "").replace("  ", " ").strip().split()

    while sentences_to_generate is None or sentences_generated < sentences_to_generate:
        # Determine the length of this sentence
        if max_length is None:
            sentence_length = random.randint(max(min_length, 1), random.randint(10, 512))
        else:
            sentence_length = random.randint(max(min_length, 1), max(max_length, min_length))

        # Generate the sentence
        sentence = []
        start_index = random.randint(0, len(words) - 1)
        while len(' '.join(sentence)) < sentence_length:
            sentence.append(words[start_index % len(words)])
            start_index += 1

        # Capitalize the first letter and add a period
        sentence[0] = sentence[0].capitalize()
        sentence = ' '.join(sentence).rstrip() + '.'

        # If the sentence is too long, truncate it
        if len(sentence) > sentence_length:
            sentence = sentence[:sentence_length - 1] + '.'

        yield sentence
        sentences_generated += 1


if __name__ == '__main__':
    # Example usage of id_guid_generator
    guid_gen = id_guid_generator(5)
    guid_ids = list(guid_gen)
    print("GUIDs:", guid_ids)

    # Example usage of id_int_generator
    int_gen = id_int_generator(5)
    int_ids = list(int_gen)
    print("Integer IDs:", int_ids)

    # Example usage of id_int_generator with odd number validation
    odd_id_gen = id_int_generator(5, validate_id=lambda x: x % 2 != 0)
    odd_ids = list(odd_id_gen)
    print("Odd IDs:", odd_ids)

    # Example usage of id_int_generator with custom start
    ids_starting_at_100_gen = id_int_generator(5, start_at=100)
    ids_starting_at_100 = list(ids_starting_at_100_gen)
    print("IDs starting at 100:", ids_starting_at_100)

    # Example usage of timestamp_generator
    timestamp_gen = timestamp_generator(3)
    timestamps = []
    for ts in timestamp_gen:
        timestamps.append(ts)
        time.sleep(1)
    print("Timestamps:", timestamps)

    print("Sentence Generator:")
    print("Default settings:")
    for sentence in sentence_generator(5):
        print(f"- {sentence}")

    print("\nCustom settings:")
    custom_gen = sentence_generator(3, min_length=50, max_length=100)
    for sentence in custom_gen:
        print(f"- {sentence}")
