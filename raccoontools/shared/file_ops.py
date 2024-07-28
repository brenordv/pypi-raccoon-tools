import json
from pathlib import Path
from typing import Union, List

from raccoontools.shared.file_utils import get_filename_for_new_file
from raccoontools.shared.serializer import obj_dump_deserializer, obj_dump_serializer


_JSON_DUMPS_PARAMS = {
    "indent": 2,
    "ensure_ascii": True
}


def load_json_from_file(file: Path, encoding: str = "utf-8") -> Union[dict, List[dict]]:
    """
    Loads a JSON file and returns the data as dict or List[dict].

    :param file: The file to load.
    :param encoding: The encoding of the file. (Default: utf-8)
    :raises ValueError: If the file is a directory.
    :raises FileNotFoundError: If the file does not exist or cannot be accessed.
    :return: The data from the file.
    """
    if file.is_dir():
        raise ValueError("The file must be a file, not a directory.")

    if not file.exists():
        raise FileNotFoundError(f"The file '{file}' does not exist or I cannot access it.")

    with open(file, "r", encoding=encoding) as f:
        return json.load(f, object_hook=obj_dump_deserializer)


def save_json_to_file(
        data: Union[dict, List[dict]],
        target_file_or_folder: Path,
        dump_kwargs: dict = None,
        encoding: str = "utf-8"
) -> Path:
    """
    Saves a dict or List[dict] to a JSON file.
    :param data: The data to save.
    :param target_file_or_folder: The file or folder to save the data. If the value passed is a folder, will
    automatically generate a unique (and sortable) filename.
    :param dump_kwargs: The kwargs to pass to the json.dump function. If you want to use the defaults values, you can
    pass an empty dictionary in this argument. (Default: indent=2, ensure_ascii=True)
    :param encoding: The encoding of the file. (Default: utf-8)
    :raises ValueError: If data or target_file_or_folder is None.
    :return: The file where the data was saved.
    """
    if any(arg is None for arg in [data, target_file_or_folder]):
        raise ValueError("Both data and target_file_or_folder must be informed.")

    if dump_kwargs is None:
        dump_kwargs = _JSON_DUMPS_PARAMS

    if target_file_or_folder.is_dir():
        filename = get_filename_for_new_file("json")
        file = target_file_or_folder.joinpath(filename)
    else:
        file = target_file_or_folder

    with open(file, "w", encoding=encoding) as f:
        json.dump(data, f, default=obj_dump_serializer, **dump_kwargs)

    return file
