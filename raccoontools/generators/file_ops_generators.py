import csv
from pathlib import Path
from typing import Union, Generator, Optional, List, Tuple


class CsvRowMetadata:
    """
    Metadata for a CSV row.
    """

    """Index of the row in the file."""
    index: int

    """Line number of the row in the file. Starts at 1, won't take headers into account."""
    data_line_number: int

    """Absolute line number of the row in the file. Will take headers into account."""
    absolute_line_number: int

    """Raw data of the row."""
    raw_data: str

    """List of headers if present."""
    headers: Optional[List[str]] = None

    def __init__(self, index: int = 0, data_line_number: int = 0, absolute_line_number: int = 0,
                 raw_data: str = "", headers: Optional[List[str]] = None):
        self.index = index
        self.data_line_number = data_line_number
        self.absolute_line_number = absolute_line_number
        self.raw_data = raw_data
        self.headers = headers


def read_line(file: Union[str, Path], strip_line: bool = True, encoding: str = "utf-8",
              buffer_size: Optional[int] = None) -> Generator[str, None, None]:
    """
    Read a file line by line.

    Args:
        file (Union[str, Path]): Path to the file.
        strip_line (bool): Strip whitespace from the beginning and end of each line. Defaults to True.
        encoding (str): File encoding. Defaults to 'utf-8'.
        buffer_size (Optional[int]): Size of the read buffer in bytes. If None, the default system buffer is used.

    Yields:
        str: Each line from the file, stripped if strip_line is True.

    Raises:
        IOError: If there's an error opening or reading the file.

    Notes:
        Suggested buffer sizes based on file size:
        - Small files (< 1 MB): None (use system default)
        - Medium files (1 MB - 100 MB): 8192 (8 KB) to 65536 (64 KB)
        - Large files (100 MB - 1 GB): 131072 (128 KB) to 524288 (512 KB)
        - Very large files (> 1 GB): 1048576 (1 MB) to 4194304 (4 MB)

        If not specified, the default Python will try to identify the file type. If it detects that it is binary,
        it will use a default value of approximately 128 kb, and if it detects that it is text, it will read line
        by line.

        These are general suggestions and may need adjustment based on specific use cases and system resources. You
        might not need that even with large files. If you're dealing with large files, play around with those values
        to see if it has any impact on performance.
    """
    try:
        with open(
                file,
                "r",
                encoding=encoding,
                buffering=buffer_size if buffer_size is not None else -1) as f:
            for line in f:
                yield line.strip() if strip_line else line
    except IOError as e:
        raise IOError(f"Error reading file {file}: {str(e)}")


def read_csv(file: Union[str, Path], encoding: str = "utf-8", has_headers: bool = True,
              buffer_size: Optional[int] = None) -> Generator[Tuple[Union[dict, list], CsvRowMetadata], None, None]:
    """
    Read a csv file row by row.

    Args:
        file (Union[str, Path]): Path to the file.
        encoding (str): File encoding. Defaults to 'utf-8'.
        has_headers (bool): If true, will assume the first line of the file is the header row. Defaults to True.
        buffer_size (Optional[int]): Size of the read buffer in bytes. If None, the default system buffer is used.

    Yields:
        (dict, CsvRowMetadata): Each line yielded as a dictionary with headers as keys and data as values or a list
        of values if no headers are present. And some with metadata.

    Raises:
        IOError: If there's an error opening or reading the file.

    Notes:
        Suggested buffer sizes based on file size:
        - Small files (< 1 MB): None (use system default)
        - Medium files (1 MB - 100 MB): 8192 (8 KB) to 65536 (64 KB)
        - Large files (100 MB - 1 GB): 131072 (128 KB) to 524288 (512 KB)
        - Very large files (> 1 GB): 1048576 (1 MB) to 4194304 (4 MB)

        These are general suggestions and may need adjustment based on specific use cases and system resources. You
        might not need that even with large files. If you're dealing with large files, play around with those values
        to see if it has any impact on performance.
    """
    headers: Optional[List[str]] = None
    data_line_number = 0

    for row_index, raw_line in enumerate(
            read_line(file, encoding=encoding, strip_line=False, buffer_size=buffer_size),
        start=1
    ):
        line_without_newline = raw_line.rstrip("\r\n").lstrip("\ufeff")

        if not line_without_newline:
            continue

        try:
            parsed_row = next(csv.reader([line_without_newline]))
        except csv.Error as exc:
            raise ValueError(f"Error parsing CSV file '{file}' at row index {row_index}: {exc}") from exc

        if not parsed_row:
            continue

        if parsed_row and parsed_row[0]:
            parsed_row[0] = parsed_row[0].lstrip("\ufeff")

        if headers is None and has_headers:
            headers = parsed_row
            continue

        if headers is not None:
            row_data = {
                header: parsed_row[idx] if idx < len(parsed_row) else None
                for idx, header in enumerate(headers)
            }
            metadata_headers = list(headers)
        else:
            row_data = parsed_row
            metadata_headers = None

        data_line_number += 1

        metadata = CsvRowMetadata(
            index=row_index,
            data_line_number=data_line_number,
            absolute_line_number=row_index + 1,
            raw_data=line_without_newline,
            headers=metadata_headers
        )

        yield row_data, metadata

if __name__ == '__main__':
    for row, mtd in read_csv("Z:\dev\projects\python\movie-recommendation\data\historical_data\letterboxd\watched.csv"):
        print(row)