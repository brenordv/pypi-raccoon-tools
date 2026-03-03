import json
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone

    UTC = timezone.utc

import pytest

from raccoontools.shared.file_ops import load_json_from_file, save_json_to_file


class TestLoadJsonFromFile:
    def test_loads_dict(self, tmp_path):
        file = tmp_path / "data.json"
        file.write_text('{"key": "value"}', encoding="utf-8")

        result = load_json_from_file(file)
        assert result["key"] == "value"

    def test_loads_list(self, tmp_path):
        file = tmp_path / "data.json"
        file.write_text('[{"a": 1}, {"b": 2}]', encoding="utf-8")

        result = load_json_from_file(file)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_raises_on_directory(self, tmp_path):
        with pytest.raises(ValueError, match="not a directory"):
            load_json_from_file(tmp_path)

    def test_raises_on_missing_file(self, tmp_path):
        missing = tmp_path / "nope.json"
        with pytest.raises(FileNotFoundError):
            load_json_from_file(missing)


class TestSaveJsonToFile:
    def test_saves_dict_to_file(self, tmp_path):
        file = tmp_path / "out.json"
        data = {"name": "test", "value": 42}

        result = save_json_to_file(data, file)
        assert result == file
        assert file.exists()

        loaded = json.loads(file.read_text(encoding="utf-8"))
        assert loaded["name"] == "test"

    def test_saves_list_to_file(self, tmp_path):
        file = tmp_path / "out.json"
        data = [{"a": 1}, {"b": 2}]

        save_json_to_file(data, file)
        loaded = json.loads(file.read_text(encoding="utf-8"))
        assert len(loaded) == 2

    def test_auto_generates_filename_for_directory(self, tmp_path):
        data = {"key": "val"}
        result = save_json_to_file(data, tmp_path)

        assert result.parent == tmp_path
        assert result.suffix == ".json"
        assert result.exists()

    def test_raises_on_none_data(self, tmp_path):
        with pytest.raises(ValueError, match="must be informed"):
            save_json_to_file(None, tmp_path / "out.json")

    def test_raises_on_none_target(self):
        with pytest.raises(ValueError, match="must be informed"):
            save_json_to_file({"a": 1}, None)

    def test_custom_dump_kwargs(self, tmp_path):
        file = tmp_path / "compact.json"
        data = {"key": "value"}

        save_json_to_file(
            data, file, dump_kwargs={"indent": None, "ensure_ascii": False}
        )
        content = file.read_text(encoding="utf-8")
        # No indentation means no newlines inside the object
        assert "\n" not in content.strip() or content.count("\n") <= 1


class TestLoadJsonObjectHook:
    def test_default_hook_coerces_numeric_strings(self, tmp_path):
        """Default behavior: string '42' is coerced to int 42."""
        file = tmp_path / "data.json"
        file.write_text('{"zip_code": "90210"}', encoding="utf-8")

        result = load_json_from_file(file)
        assert result["zip_code"] == 90210
        assert isinstance(result["zip_code"], int)

    def test_none_hook_preserves_strings(self, tmp_path):
        """Bug 10 fix: passing None disables type coercion."""
        file = tmp_path / "data.json"
        file.write_text('{"zip_code": "90210"}', encoding="utf-8")

        result = load_json_from_file(file, object_hook=None)
        assert result["zip_code"] == "90210"
        assert isinstance(result["zip_code"], str)

    def test_none_hook_preserves_date_strings(self, tmp_path):
        file = tmp_path / "data.json"
        file.write_text('{"date": "2024-01-15"}', encoding="utf-8")

        result = load_json_from_file(file, object_hook=None)
        assert result["date"] == "2024-01-15"
        assert isinstance(result["date"], str)

    def test_custom_hook(self, tmp_path):
        """Callers can provide their own object_hook."""
        file = tmp_path / "data.json"
        file.write_text('{"key": "value"}', encoding="utf-8")

        def upper_values(obj):
            return {k: v.upper() if isinstance(v, str) else v for k, v in obj.items()}

        result = load_json_from_file(file, object_hook=upper_values)
        assert result["key"] == "VALUE"


class TestRoundTrip:
    def test_dict_round_trip(self, tmp_path):
        file = tmp_path / "round.json"
        original = {"name": "test", "count": 42}

        save_json_to_file(original, file)
        loaded = load_json_from_file(file)

        assert loaded["name"] == "test"
        # Note: count may be deserialized as int due to obj_dump_deserializer
        assert loaded["count"] == 42
