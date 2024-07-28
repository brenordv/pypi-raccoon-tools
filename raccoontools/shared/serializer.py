from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Union, List
from pydantic import BaseModel
import csv


_PATH_LIB_OBJ_TAG = "[PATHLIBOBJ]"


def obj_to_dict(obj) -> dict:
    """
    Tries to convert an object to dict
    :param obj: Object that we'll try to convert to dict.
    :return: Dict representation of the object.
    :raises ValueError: If the object can't be converted to a dict.
    """

    if issubclass(type(obj), BaseModel):
        # If it's a BaseModel, convert it to a dict using that fancy helper.
        obj = obj.dict()

    elif hasattr(obj, '__dict__'):
        # If it's an object, convert it to a dict using the __dict__ attribute.
        obj = obj.__dict__
    else:
        # Else: No idea how to convert it to a dict, so just return it as is.
        raise ValueError(f"Could not convert object of type {type(obj)} to a dict.")

    # Return the (hopefully) converted object.
    return obj


def serialize_to_dict(obj) -> Union[dict, List[dict], None]:
    """
    Serialize obj to a dict or a list of dicts. Useful when sending complex objects in http requests.
    If the obj passed is a dict, will iterate over all the properties and convert them to dicts.
    Remarks: This scans the object recursively.

    :param obj: The object to be serialized
    :return: The serialized JSON object or None if the object is None.
    """
    if obj is None:
        return None

    if isinstance(obj, list):
        serialized = [obj_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        serialized = {}
        for key, value in obj.items():
            serialized[key] = serialize_to_dict(value)
    else:
        serialized = obj_to_dict(obj)

    return serialized


def parse_csv(csv_data: str) -> List[dict]:
    """
    Parses a CSV string and returns a list of dictionaries.

    :param csv_data: The CSV string.
    :return: A list of dictionaries.
    """
    csv_file = StringIO(csv_data)
    reader = csv.DictReader(csv_file)
    return [row for row in reader]


def csv_string_to_dict_list(
        data: Union[str, List[str], dict, List[dict]],
        no_data_return: str = "No data available"
) -> Union[List[dict], str]:
    """
    Converts a CSV string to a list of dictionaries.
    The first row is considered the header row.
    :param no_data_return: The value to return if no data is available.
    :param data: The CSV string.
    :return: A list of dictionaries or the no_data_return value if no data is available.
    """
    if isinstance(data, str):
        return parse_csv(data)
    elif isinstance(data, list):
        result = []
        [result.extend(csv_string_to_dict_list(d)) for d in data]
        return result

    return no_data_return


def dataset_to_prompt_text(dataset: List[dict]) -> str:
    """
    Converts a dataset to a prompt text.
    :param dataset: The dataset.
    :return: The prompt text.
    """
    if dataset is None or not isinstance(dataset, list):
        return str(dataset)

    data = []
    for row in dataset:
        item ={}
        for key, value in row.items():
            if isinstance(value, datetime):
                item[key] = value.strftime("%Y-%m-%d %H:%M:%S.%f")
                continue

            item[key] = value

        data.append(item)

    return str(data)


def obj_dump_serializer(obj):
    """
    Used to serialize objects when saving data to file.

    Remarks:
    - Datetime objects are serialized to iso format.
    - When serializing an object of type Path, it will convert by saving the absolute path of the object with a tag that
     will be used for deserialization.

    :param obj: The object to serialize.
    :return: The serialized object.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Path):
        return f"{_PATH_LIB_OBJ_TAG}{obj.absolute()}"
    elif isinstance(obj, set):
        return list(obj)

    return obj


def obj_dump_deserializer(obj):
    """
    Used to deserialize objects when loading data from file.

    Remarks:
    - Datetime objects are deserialized from iso format.
    - When deserializing an object of type Path, it will convert by loading the path from the string with the tag. This
    does not check or guarantee that the path exists.

    :param obj: The object to deserialize.
    :return: The deserialized object.
    """
    if isinstance(obj, dict):
        return {k: obj_dump_deserializer(v) for k, v in obj.items()}

    if not isinstance(obj, str):
        return obj

    try:
        return datetime.fromisoformat(obj)
    except (TypeError, ValueError):
        pass

    if obj.startswith(_PATH_LIB_OBJ_TAG):
        path = Path(obj.split(_PATH_LIB_OBJ_TAG)[1])
        return path

    return obj
