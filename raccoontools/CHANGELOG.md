# Changelog

## [3.6.0]

### Added
- `comparators.dict_comparators`: New comparison helpers for dictionaries and lists of dictionaries.
  - `dicts_are_equal` / `compare_dicts`: deep, key-order-independent dictionary comparison. `compare_dicts` returns a `DictComparison` named tuple with `are_equal` and a `DictDiff` (`added` / `removed` / `changed`) keyed by dotted paths (e.g. `"user.address.zip"`). Nested dictionaries are recursed into; every other value (including nested lists, `datetime`, and custom types) is compared as an opaque leaf.
  - `dict_lists_are_equal` / `compare_dict_lists`: order-independent `list[dict]` comparison (the lists are treated as multisets, so duplicates are counted). `compare_dict_lists` returns a `DictListComparison` with `only_in_a` / `only_in_b`.
  - The `*_are_equal` functions delegate to their `compare_*` counterparts, so the boolean and detailed results can never disagree. All functions raise `TypeError` for invalid input types.

## [3.5.0]

### Added
- `string_utils.linefy`: New string helper that collapses a multi-line string into a single line. Removes all linebreaks, merges sequential whitespace runs into a single space, and trims the ends. Raises `TypeError` for non-string input.

## [3.4.0]

### Changed
- `load_json_from_file` and `save_json_to_file` now accept a string path in addition to a `Path` for the file/folder argument. `save_json_to_file` raises `ValueError` if the target is an empty (or whitespace-only) string.
- `get_date_based_subfolder` now accepts a string path in addition to a `Path` for `ref_path`.
- Bumped `idna` to `3.18`. (Not directly used in the repo. Added to solve security vulnerabilities surfaced by the use of `requests`.)

## [3.3.1]
- Security update. Added `idna` as explicit dependency to address security vulnerabilities surfaced by the use of `requests`. Will remove as soon as `requests` catches up.

## [3.3.0]

### Added
- `timedelta_to_readable_elapsed_time`: New converter that formats a `timedelta` as a human-readable elapsed time string (e.g. `"2 days and 5 hours ago"`). Supports configurable suffix, zero-delta label, and a `zero_delta_threshold` parameter to control when seconds-level detail is shown vs. returning a label like `"just now"`.
- `time_value_to_readable_elapsed_time`: Convenience wrapper that accepts a numeric value and unit (e.g. `3600, "seconds"` or `2, "days"`) and delegates to `timedelta_to_readable_elapsed_time`.

## [3.2.1]
- Re-added `"urllib3==2.7.0"` to solve security vulnerabilities. Package actually used by `requests`.
- Updated `requests` to `2.24.1`.

## [3.2.0]
- Updated `requests` to `2.24.0`.

## [3.1.0]

### Added
- `timestamp_to_datetime`: New converter that turns numeric timestamps (seconds, milliseconds, microseconds, or nanoseconds) into timezone-aware `datetime` objects. Uses integer arithmetic for `int` inputs to avoid IEEE-754 float rounding. Defaults to milliseconds and UTC.

## [3.0.0]
Dropped support for Python 3.10. Minimum required version is now Python 3.11.

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
