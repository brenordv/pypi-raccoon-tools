from datetime import datetime, UTC
from pathlib import Path

import pytest
from pydantic import BaseModel

from raccoontools.shared.serializer import (
    csv_string_to_dict_list,
    dataset_to_prompt_text,
    obj_dump_deserializer,
    obj_dump_serializer,
    obj_to_dict,
    parse_csv,
    serialize_to_dict,
)


# ---------------------------------------------------------------------------
# obj_to_dict
# ---------------------------------------------------------------------------
class TestObjToDict:
    def test_pydantic_model(self):
        """Bug 4 regression: must use model_dump, not .dict()."""

        class MyModel(BaseModel):
            name: str
            value: int

        model = MyModel(name="test", value=42)
        result = obj_to_dict(model)
        assert result == {"name": "test", "value": 42}

    def test_plain_object_with_dict(self):
        class Simple:
            def __init__(self):
                self.x = 1
                self.y = 2

        result = obj_to_dict(Simple())
        assert result == {"x": 1, "y": 2}

    def test_raises_on_primitive(self):
        with pytest.raises(ValueError, match="Could not convert"):
            obj_to_dict(42)

    def test_raises_on_string(self):
        with pytest.raises(ValueError, match="Could not convert"):
            obj_to_dict("hello")


# ---------------------------------------------------------------------------
# serialize_to_dict
# ---------------------------------------------------------------------------
class TestSerializeToDict:
    def test_none_returns_none(self):
        assert serialize_to_dict(None) is None

    def test_list_of_pydantic_models(self):
        class Item(BaseModel):
            name: str

        items = [Item(name="a"), Item(name="b")]
        result = serialize_to_dict(items)
        assert result == [{"name": "a"}, {"name": "b"}]

    def test_dict_passthrough(self):
        result = serialize_to_dict({"key": "value"})
        assert result["key"] == "value"

    def test_nested_dict(self):
        class Inner(BaseModel):
            val: int

        data = {"inner": Inner(val=5)}
        result = serialize_to_dict(data)
        assert result["inner"] == {"val": 5}

    def test_dict_preserves_int_values(self):
        """Bug 7 regression: int values must not be converted to strings."""
        result = serialize_to_dict({"count": 42})
        assert result["count"] == 42
        assert isinstance(result["count"], int)

    def test_dict_preserves_float_values(self):
        """Bug 7 regression: float values must not be converted to strings."""
        result = serialize_to_dict({"score": 9.5})
        assert result["score"] == 9.5
        assert isinstance(result["score"], float)

    def test_dict_preserves_bool_values(self):
        """Bug 7 regression: bool values must not be converted to strings."""
        result = serialize_to_dict({"active": True, "deleted": False})
        assert result["active"] is True
        assert result["deleted"] is False

    def test_dict_preserves_string_values(self):
        result = serialize_to_dict({"name": "Alice"})
        assert result["name"] == "Alice"
        assert isinstance(result["name"], str)

    def test_dict_preserves_mixed_primitives(self):
        """Bug 7 regression: all primitive types preserved in a single dict."""
        data = {"name": "Alice", "age": 30, "active": True, "score": 9.5}
        result = serialize_to_dict(data)
        assert result == data


# ---------------------------------------------------------------------------
# obj_dump_serializer
# ---------------------------------------------------------------------------
class TestObjDumpSerializer:
    def test_datetime_to_iso(self):
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        result = obj_dump_serializer(dt)
        assert "2024-01-15" in result

    def test_path_serialization(self):
        p = Path("/tmp/test.txt")
        result = obj_dump_serializer(p)
        assert result.startswith("[PATHLIBOBJ]")
        assert "test.txt" in result

    def test_set_sorted(self):
        result = obj_dump_serializer({3, 1, 2})
        assert result == ["1", "2", "3"]

    def test_string_passthrough(self):
        assert obj_dump_serializer("hello") == "hello"

    def test_deep_serialization_list(self):
        dt = datetime(2024, 1, 1, tzinfo=UTC)
        result = obj_dump_serializer([dt, "text"])
        assert isinstance(result, list)
        assert "2024-01-01" in result[0]
        assert result[1] == "text"

    def test_deep_serialization_dict(self):
        result = obj_dump_serializer({"key": "val"})
        assert result == {"key": "val"}

    def test_non_serializable_raises(self):
        class Unserializable:
            def __str__(self):
                raise RuntimeError("nope")

        with pytest.raises(TypeError, match="not serializable"):
            obj_dump_serializer(Unserializable())


# ---------------------------------------------------------------------------
# obj_dump_deserializer
# ---------------------------------------------------------------------------
class TestObjDumpDeserializer:
    def test_datetime_string(self):
        result = obj_dump_deserializer("2024-01-15T10:30:00+00:00")
        assert isinstance(result, datetime)

    def test_int_string(self):
        result = obj_dump_deserializer("42")
        assert result == 42
        assert isinstance(result, int)

    def test_float_string(self):
        result = obj_dump_deserializer("3.14")
        assert result == 3.14
        assert isinstance(result, float)

    def test_path_string(self):
        result = obj_dump_deserializer("[PATHLIBOBJ]/tmp/test.txt")
        assert isinstance(result, Path)

    def test_plain_string(self):
        result = obj_dump_deserializer("hello world")
        assert result == "hello world"

    def test_dict_recursion(self):
        result = obj_dump_deserializer({"count": "42", "name": "test"})
        assert result["count"] == 42
        assert result["name"] == "test"


# ---------------------------------------------------------------------------
# parse_csv / csv_string_to_dict_list
# ---------------------------------------------------------------------------
class TestParseCsv:
    def test_basic_csv(self):
        csv_data = "name,age\nAlice,30\nBob,25"
        result = parse_csv(csv_data)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["age"] == "25"

    def test_empty_csv(self):
        result = parse_csv("")
        assert result == []


class TestCsvStringToDictList:
    def test_string_input(self):
        result = csv_string_to_dict_list("name,age\nAlice,30")
        assert isinstance(result, list)
        assert result[0]["name"] == "Alice"

    def test_list_of_strings(self):
        data = ["name,age\nAlice,30", "name,age\nBob,25"]
        result = csv_string_to_dict_list(data)
        assert len(result) == 2

    def test_non_string_non_list_returns_default(self):
        result = csv_string_to_dict_list(42)
        assert result == "No data available"

    def test_custom_no_data_return(self):
        result = csv_string_to_dict_list(42, no_data_return="N/A")
        assert result == "N/A"


# ---------------------------------------------------------------------------
# dataset_to_prompt_text
# ---------------------------------------------------------------------------
class TestDatasetToPromptText:
    def test_basic_dataset(self):
        data = [{"name": "Alice", "age": 30}]
        result = dataset_to_prompt_text(data)
        assert "Alice" in result
        assert "30" in result

    def test_with_datetime(self):
        dt = datetime(2024, 1, 15, 10, 30, 0)
        data = [{"timestamp": dt}]
        result = dataset_to_prompt_text(data)
        assert "2024-01-15" in result

    def test_none_returns_string(self):
        assert dataset_to_prompt_text(None) == "None"

    def test_non_list_returns_string(self):
        assert dataset_to_prompt_text("hello") == "hello"
