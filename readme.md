# Raccoon Tools
This is a collection of tools that I regularly use on several projects. To stop duplicating and to (hopefully) help
someone, I decided to make them into a public package.

# Functionalities
## Decorators

### `retry`
A decorator that retries a function call a specified number of times before giving up. 
It logs each attempt and the final failure if all retries are exhausted.

**Parameters:**
- `retries`: Maximum number of retries before giving up (default: 3).
- `delay`: Delay in seconds between each retry (default: 1).
- `delay_is_exponential`: If True, the delay between retries will increase exponentially (default: False).
- `only_exceptions_of_type`: A list of exception types to catch and retry on. If None, all exceptions are caught.
- `log_level`: The log level used by the decorator (default: logging.ERROR).

### `retry_request`
Like the previous decorator, but for HTTP requests. 
It logs each attempt and the final failure if all retries are exhausted. 
It also provides options to handle specific HTTP status codes.

**Parameters:**
- `retries`: Maximum number of retries before giving up (default: 3).
- `delay`: Delay in seconds between each retry (default: 1).
- `delay_is_exponential`: If True, the delay between retries will increase exponentially (default: False).
- `skip_retry_on_404`: If True, the decorator will not retry on 404 responses (default: False).
- `retry_only_on_status_codes`: A list of HTTP status codes to retry on. If None, no retries will be made.
- `get_new_token_on_401`: An optional callable to execute and get a new token when a 401 response is received.
- `get_new_token_on_403`: An optional callable to execute and get a new token when a 403 response is received.
- `log_level`: The log level used by the decorator (default: logging.ERROR).

### `benchmark`
A decorator that benchmarks the execution time of a function. 
The results are logged using the logging module at the INFO level. 
The decorated function can also provide benchmark information via the `get_benchmark_info` method.

## Generators

### `infinite_iterator`
Generates an infinite iterator from a list.

**Parameters:**
- `list_to_iterate_over`: The list to iterate over.

### `read_line`
Reads a file line by line.

**Parameters:**
- `file`: Path to the file.
- `strip_line`: Strip whitespace from the beginning and end of each line (default: True).
- `encoding`: File encoding (default: 'utf-8').
- `buffer_size`: Size of the read buffer in bytes. If None, the default system buffer is used.

### `id_guid_generator`
Generates unique GUID (Globally Unique Identifier) strings.

**Parameters:**
- `ids_to_generate`: The number of GUIDs to generate. If None, generates indefinitely.

### `id_int_generator`
Generates integer IDs with optional validation.

**Parameters:**
- `ids_to_generate`: The number of IDs to generate. If None, generates indefinitely.
- `start_at`: The starting value for the ID sequence (default: 0).
- `validate_id`: A function to validate each ID. If None, all IDs are considered valid.

### `timestamp_generator`
Generates Unix timestamps.

**Parameters:**
- `timestamps_to_generate`: The number of timestamps to generate. If None, generates indefinitely.

### `sentence_generator`
Generates Lorem Ipsum sentences with lengths ranging from min_length to max_length.

**Parameters:**
- `sentences_to_generate`: The number of sentences to generate. If None, generates indefinitely.
- `min_length`: The minimum length of each sentence (default: 1).
- `max_length`: The maximum length of each sentence. If None, a random value between 10 and 512 is used for each sentence.

## Shared Utilities

### `file_ops`
Provides functions to load and save JSON data to and from files.

- `load_json_from_file(file: Path, encoding: str = "utf-8") -> Union[dict, List[dict]]`: Loads a JSON file and returns the data as a dictionary or list of dictionaries.
- `save_json_to_file(data: Union[dict, List[dict]], target_file_or_folder: Path, dump_kwargs: dict = None, encoding: str = "utf-8") -> Path`: Saves a dictionary or list of dictionaries to a JSON file.

### `file_utils`
Provides utility functions for file operations.

- `get_filename_for_new_file(file_extension: str, prefix: str = None, add_current_datetime_as_format: str = "%Y%m%d%H%M%S%f", use_utc: bool = True, unique_identifier: Tuple[str, bool] = True, part_separator: str = "-", suffix: str = None) -> str`: Generates a unique filename for a new file.

### `http`
Provides utility functions for HTTP headers.

- `get_headers(token: str, content_type: str = "application/json", user_agent: str = None, fake_browser_user_agent: bool = False, extra_args: Dict[str, str] = None) -> Dict[str, str]`: Generates headers for an HTTP request.

### `requests_with_retry`
A wrapper around requests using the `retry_request` decorator.

- `get(url, params=None, **kwargs) -> requests.Response`: Sends a GET request with retry functionality.
- `options(url, **kwargs) -> requests.Response`: Sends an OPTIONS request with retry functionality.
- `head(url, **kwargs) -> requests.Response`: Sends a HEAD request with retry functionality.
- `post(url, data=None, json=None, **kwargs) -> requests.Response`: Sends a POST request with retry functionality.
- `put(url, data=None, **kwargs) -> requests.Response`: Sends a PUT request with retry functionality.
- `patch(url, data=None, **kwargs) -> requests.Response`: Sends a PATCH request with retry functionality.
- `delete(url, **kwargs) -> requests.Response`: Sends a DELETE request with retry functionality.

### `serializer`
Provides functions to serialize and deserialize objects.

- `serialize_to_dict(obj) -> Union[dict, List[dict], None]`: Serializes an object to a dictionary or list of dictionaries.
- `parse_csv(csv_data: str) -> List[dict]`: Parses a CSV string and returns a list of dictionaries.
- `csv_string_to_dict_list(data: Union[str, List[str], dict, List[dict]], no_data_return: str = "No data available") -> Union[List[dict], str]`: Converts a CSV string to a list of dictionaries.
- `dataset_to_prompt_text(dataset: List[dict]) -> str`: Converts a dataset to a prompt text.
- `obj_dump_serializer(obj)`: Serializes objects for saving data to a file.
- `obj_dump_deserializer(obj)`: Deserializes objects when loading data from a file.

# Changelog
- [Check the changelog here.](changelog.md)
