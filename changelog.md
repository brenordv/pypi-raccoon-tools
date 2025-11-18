# Changelog
## [1.2.0]
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
