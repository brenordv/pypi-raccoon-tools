from pathlib import Path
from typing import Union, Generator, Optional


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

        These are general suggestions and may need adjustment based on specific use cases and system resources. You
        might not need that even with large files. If you're dealing with large files, play around with those values
        to see if it has any impact on performance.
    """
    try:
        with open(file, "r", encoding=encoding, buffering=buffer_size) as f:
            for line in f:
                yield line.strip() if strip_line else line
    except IOError as e:
        raise IOError(f"Error reading file {file}: {str(e)}")
