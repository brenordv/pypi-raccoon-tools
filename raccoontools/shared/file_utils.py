from datetime import datetime
from typing import Tuple
from uuid import uuid4


def get_filename_for_new_file(
        file_extension: str,
        prefix: str = None,
        add_current_datetime_as_format: str = "%Y%m%d%H%M%S%f",
        use_utc: bool = True,
        unique_identifier: Tuple[str, bool] = True,
        part_separator: str = "-",
        suffix: str = None
) -> str:
    """
    Generates a filename for a new file.
    Presumably, this is will be unique.

    :param file_extension: The extension of the file.
    :param prefix: Will be added to the beginning of the filename. (Optional)
    :param add_current_datetime_as_format: If informed, will add the current datetime to the filename in the
    desired format. (Default: %Y%m%d%H%M%S%f)
    :param use_utc: If True, will use the UTC timezone. Have no effect if add_current_datetime_as_format is None.
     (Default: True)
    :param unique_identifier: If true, will add a new uuid4 to the filename. You can also pass the desired identifier.
    (Default: True)
    :param part_separator: The separator to use between the parts of the filename. (Default: "-")
    :param suffix: Will be added to the end of the filename. (Optional)
    :return: The filename.
    """
    filename_parts = []

    if prefix:
        filename_parts.append(prefix)

    if add_current_datetime_as_format:
        now = datetime.utcnow() if use_utc else datetime.now()
        current_datetime = now.strftime(add_current_datetime_as_format)
        filename_parts.append(current_datetime)

    if unique_identifier:
        filename_parts.append(str(uuid4()) if unique_identifier is True else unique_identifier)

    if suffix:
        filename_parts.append(suffix)

    ext = file_extension if file_extension.startswith(".") else f".{file_extension}"

    filename = f"{part_separator.join(filename_parts)}{ext}"

    return filename
