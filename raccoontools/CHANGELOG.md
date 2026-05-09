# Changelog
## [2.0.1]
Nothing changed in the code. Just fixed the readme.md file.

## [2.0.0]
### Breaking changes
- Dropped Python 3.9 support. The minimum required version is now Python 3.10.

### General
- Modernized type hints across the codebase: replaced `Union`, `Optional`, `List`, `Dict`, `Tuple`, and `Type` from `typing` with PEP 604 (`X | Y`) and PEP 585 (`list`, `dict`, `tuple`, `type`) syntax.
- Replaced `datetime.UTC` compatibility shim (`try/except ImportError`) with direct `timezone.utc` usage.
- Updated CI pipeline to test Python 3.10–3.15 (removed 3.9).
- Updated PyPI classifiers to reflect supported Python versions (3.10–3.14).
- Removed `typing-extensions` as a direct dependency (replaced `typing_extensions.TypedDict` with `typing.TypedDict`, available since Python 3.8).
- Updated `requests` and `urllib3` dependency versions to address security vulnerabilities.

### Bug fixes
- `read_csv`: Fixed off-by-one error in `absolute_line_number` metadata (was reporting one line too high).

### Added
- `get_date_based_subfolder`: New utility to create/get date-based subdirectories with configurable format, UTC support, and delta offsets.

## [1.3.1]
### Bug fixes
- `obj_to_dict`: Fixed `dict` inputs not being recognized as valid — dicts are now returned as-is instead of raising `ValueError`.
- `obj_to_dict`: Added a specific error message when `list` or `tuple` is passed (previously raised a generic error).
- `sentence_generator`: Fixed flaky sentence generation where `min_length=1` could produce a period-only string (`'.'`), causing the first character to not be uppercase.

## [1.3.0]
### General
- Updated dependency versions.
- Replaced `utcnow()` with `now(tz=UTC)`.
- Added `datetime.UTC` compatibility shim for Python 3.9/3.10 (where `UTC` is not available).
- Removed stale `setup.py`; `pyproject.toml` is now the single source of truth.
- Updated CI pipeline to run tests across Python 3.9–3.14 before publishing.
- Bumped GitHub Actions (`actions/checkout` v4, `actions/setup-python` v5).

### Bug fixes
- `retry`: Fixed decorator silently swallowing the last exception and returning `None` instead of re-raising.
- `retry_request`: Fixed `send_json_as_is` kwarg leaking into `requests.post`/`put`/`patch`, causing `TypeError`.
- `sentence_generator`: Fixed `ValueError` crash when `min_length` exceeded the random upper bound.
- `obj_to_dict`: Replaced deprecated Pydantic v1 `.dict()` with `.model_dump()`.
- `get_headers`: Fixed `Authorization: Bearer None` being emitted when token is `None` or empty.
- `get_filename_for_new_file`: Fixed incorrect type hint (`Tuple[str, bool]` → `Union[str, bool]`).
- `serialize_to_dict`: Fixed primitive dict values (`int`, `float`, `bool`) being silently converted to strings.
- `csv_string_to_dict_list`: Fixed `dict` and `List[dict]` inputs causing character explosion; dicts are now passed through as-is.

### Added
- `load_json_from_file`: Added optional `object_hook` parameter to control JSON deserialization. Pass `None` to disable automatic type coercion (numeric strings, dates).
- Comprehensive test suite covering all modules.

## [1.2.1]
### General
- Updated dependency versions.

## [1.2.0]
### General
- Updated documentation.
- Updated dependency versions.

### Added generators
- `read_csv`: Read CSV files into a list of dictionaries + metadata, line by line.

### Bug fixes
- `read_line`: Fixed bug related to the default value for `buffer_size` parameter.

## [1.1.1]
### Bug fixes
- `serialize_to_dict`: Fixed bug when serializing simple objects.
- `obj_dump_serializer`: Improved usability;
- `obj_dump_deserializer`: Improved usability;

## [1.1.0]
### Added generators
- `infinite_iterator` generator to create an infinite iterator from a list.
- `read_line` generator to read a file line by line.
- `id_guid_generator` to generate unique GUID strings.
- `id_int_generator` to generate integer IDs with optional validation.
- `timestamp_generator` to generate Unix timestamps.
- `sentence_generator` to generate Lorem Ipsum 

## [1.0.0]
- Initial version of the package
