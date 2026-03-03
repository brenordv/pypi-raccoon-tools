# Changelog
## [1.3.0]
### General
- Updated dependency versions.
- Replaced `utcnow()` with `now(tz=UTC)`.
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
