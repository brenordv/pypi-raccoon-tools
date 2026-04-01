from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

UTC = timezone.utc


def get_filename_for_new_file(
        file_extension: str,
        prefix: str | None = None,
        add_current_datetime_as_format: str = "%Y%m%d%H%M%S%f",
        use_utc: bool = True,
        unique_identifier: str | bool = True,
        part_separator: str = "-",
        suffix: str | None = None
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
        now = datetime.now(tz=UTC) if use_utc else datetime.now()
        current_datetime = now.strftime(add_current_datetime_as_format)
        filename_parts.append(current_datetime)

    if unique_identifier:
        filename_parts.append(str(uuid4()) if unique_identifier is True else unique_identifier)

    if suffix:
        filename_parts.append(suffix)

    ext = file_extension if file_extension.startswith(".") else f".{file_extension}"

    filename = f"{part_separator.join(filename_parts)}{ext}"

    return filename


def get_date_based_subfolder(
        ref_path: Path,
        use_utc: bool = True,
        date_ref: datetime | None = None,
        add_delta_days: int | None = None,
        date_format: str = "%Y-%m-%d",
        create_if_missing: bool = True
) -> Path:
    """
    Gets a subfolder for the reference date. Using the specified date format (by default YYYY-MM-DD).

    :param ref_path: Folder that will be used as the main folder. If a file is provided, will use the parent as the
    base. Caveat: If the path is a folder, doesn't exist, and have a dot in the name (i.e: '~/projects/my.project.data'), we'll assume it's a file.
    :param use_utc: If True, will use the UTC timezone. Only has an effect if date_ref is None.
    :param date_ref: The date to use as the reference. If None, will use the current date.
    :param add_delta_days: If informed, will add the delta days to the date.
    :param date_format: The format of the date. (Default: "%Y-%m-%d")
    :param create_if_missing: If True, will create the folder if it doesn't exist. (Default: True)
    :return: The subfolder path.
    """
    base_path = ref_path.parent if ref_path.is_file() or ref_path.suffix != "" else ref_path

    if date_ref is not None:
        target_date = date_ref
    else:
        target_date = datetime.now(tz=UTC) if use_utc else datetime.now()

    if add_delta_days is not None:
        target_date += timedelta(days=add_delta_days)

    new_folder = base_path.joinpath(target_date.strftime(date_format))

    if create_if_missing and not new_folder.exists():
        new_folder.mkdir(parents=True, exist_ok=True)

    return new_folder
