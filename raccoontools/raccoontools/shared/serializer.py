import csv
import warnings
from collections.abc import Callable
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any

from pydantic import BaseModel

_PATH_LIB_OBJ_TAG = "[PATHLIBOBJ]"

_JSON_PRIMITIVE_TYPES = (str, int, float, bool)


def obj_to_dict(obj: Any) -> dict[Any, Any]:
    """
    Tries to convert an object to dict
    :param obj: Object that we'll try to convert to dict.
    :return: Dict representation of the object.
    :raises ValueError: If the object can't be converted to a dict.
    """
    if isinstance(obj, dict):
        return obj

    if issubclass(type(obj), BaseModel):
        # If it's a BaseModel, convert it to a dict using model_dump (Pydantic v2).
        return obj.model_dump()

    if hasattr(obj, "__dict__"):
        # If it's an object, convert it to a dict using the __dict__ attribute.
        return obj.__dict__

    if isinstance(obj, (list, tuple)):
        raise ValueError(f"Could not convert object of type {type(obj)} to a dict. Lists and tuples are not supported.")

    # Else: No idea how to convert it to a dict.
    raise ValueError(f"Could not convert object of type {type(obj)} to a dict.")


def serialize_to_dict(obj: Any, obj_serializer: Callable | None = None) -> dict[Any, Any] | list[Any] | None:
    """
    Serialize obj to a dict or a list. Useful when sending complex objects in http requests.
    Dict values and list or tuple items are scanned recursively: strings, numbers, booleans and None are kept as they
    are, nested dicts, lists and tuples are serialized the same way (tuples become lists, as JSON has no tuples), and
    any other object is converted with ``obj_to_dict``.

    :param obj: The object to be serialized
    :param obj_serializer: Deprecated. This parameter is no longer used and will be removed in a future version.
    :return: The serialized JSON object or None if the object is None.
    """
    if obj is None:
        return None

    if obj_serializer is not None:
        warnings.warn(
            "The 'obj_serializer' parameter is deprecated and will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )

    if isinstance(obj, (list, tuple)):
        return [item if isinstance(item, _JSON_PRIMITIVE_TYPES) else serialize_to_dict(item) for item in obj]

    if isinstance(obj, dict):
        return {
            key: value if isinstance(value, _JSON_PRIMITIVE_TYPES) else serialize_to_dict(value)
            for key, value in obj.items()
        }

    return obj_to_dict(obj)


def parse_csv(csv_data: str) -> list[dict]:
    """
    Parses a CSV string and returns a list of dictionaries.

    :param csv_data: The CSV string.
    :return: A list of dictionaries.
    """
    csv_file = StringIO(csv_data)
    reader = csv.DictReader(csv_file)
    return [row for row in reader]


def csv_string_to_dict_list(
    data: str | list[str] | dict | list[dict], no_data_return: str = "No data available"
) -> list[dict] | str:
    """
    Converts a CSV string to a list of dictionaries.
    The first row is considered the header row.
    :param no_data_return: The value to return if no data is available.
    :param data: The CSV string.
    :return: A list of dictionaries or the no_data_return value if no data is available.
    """
    if isinstance(data, str):
        return parse_csv(data)
    elif isinstance(data, dict):
        return [data]
    elif isinstance(data, list):
        result = []
        for d in data:
            parsed = csv_string_to_dict_list(d, no_data_return=no_data_return)
            if isinstance(parsed, list):
                result.extend(parsed)
        return result

    return no_data_return


def dataset_to_prompt_text(dataset: list[dict]) -> str:
    """
    Converts a dataset to a prompt text.
    TODO: Explain a bit better what does this function do, and how to use it.
    :param dataset: The dataset.
    :return: The prompt text.
    """
    if dataset is None or not isinstance(dataset, list):
        return str(dataset)

    data = []
    for row in dataset:
        item = {}
        for key, value in row.items():
            if isinstance(value, datetime):
                item[key] = value.strftime("%Y-%m-%d %H:%M:%S.%f")
                continue

            item[key] = value

        data.append(item)

    return str(data)


def obj_dump_serializer(obj: Any, deep_serialization: bool = True, pathlib_obj_tag: str = _PATH_LIB_OBJ_TAG) -> Any:
    """
    Used to serialize objects when saving data to file.

    Remarks:
    - Datetime objects are serialized to iso format.
    - When serializing an object of type Path, it will convert by saving the absolute path of the object with a tag that
     will be used for deserialization.

    :param obj: The object to serialize.
    :param deep_serialization: If true, will serialize nested objects inside a list or set.
    :param pathlib_obj_tag: The tag to use when serializing Path objects. (Default: [PATHLIBOBJ])
    :return: The serialized object.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()

    elif isinstance(obj, Path):
        return f"{pathlib_obj_tag}{obj.absolute()}"

    elif isinstance(obj, set):
        try:
            set_as_list = sorted(obj)
        except TypeError:
            set_as_list = list(obj)

        if not deep_serialization:
            return set_as_list

        return [obj_dump_serializer(item, deep_serialization, pathlib_obj_tag) for item in set_as_list]

    elif isinstance(obj, list) and deep_serialization:
        return [obj_dump_serializer(item, deep_serialization, pathlib_obj_tag) for item in obj]

    elif isinstance(obj, dict) and deep_serialization:
        return {
            obj_dump_serializer(k, deep_serialization, pathlib_obj_tag): obj_dump_serializer(
                v, deep_serialization, pathlib_obj_tag
            )
            for k, v in obj.items()
        }

    elif isinstance(obj, str):
        return obj

    try:
        return str(obj)
    except Exception as e:
        raise TypeError(f"Object of type {type(obj)} is not serializable") from e


def obj_dump_deserializer(obj: Any, pathlib_obj_tag: str = _PATH_LIB_OBJ_TAG) -> Any:
    """
    Used to deserialize objects when loading data from file.

    Remarks:
    - Only strings are converted. Numbers, booleans, None and lists decoded by the JSON parser are returned unchanged.
    - Datetime objects are deserialized from iso format.
    - When deserializing an object of type Path, it will convert by loading the path from the string with the tag. This
    does not check or guarantee that the path exists.

    :param obj: The object to deserialize.
    :param pathlib_obj_tag: The tag to use when deserializing Path objects. (Default: [PATHLIBOBJ])
    :return: The deserialized object.
    """
    if isinstance(obj, dict):
        return {
            obj_dump_deserializer(k, pathlib_obj_tag): obj_dump_deserializer(v, pathlib_obj_tag) for k, v in obj.items()
        }

    if not isinstance(obj, str):
        return obj

    try:
        return datetime.fromisoformat(obj)
    except (TypeError, ValueError):
        pass

    try:
        return int(obj)
    except (TypeError, ValueError):
        pass

    try:
        return float(obj)
    except (TypeError, ValueError):
        pass

    if obj.startswith(pathlib_obj_tag):
        path = Path(obj[len(pathlib_obj_tag) :])
        return path

    return obj
