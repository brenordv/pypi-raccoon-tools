import codecs
from pathlib import Path

import pytest

from raccoontools.generators.file_ops_generators import read_csv, read_line


class TestReadLine:
    def test_lines_are_stripped_by_default(self, tmp_path: Path) -> None:
        text_file = tmp_path / "data.txt"
        text_file.write_text("  first  \nsecond\n", encoding="utf-8")

        assert list(read_line(text_file)) == ["first", "second"]

    def test_lines_keep_whitespace_when_strip_is_disabled(self, tmp_path: Path) -> None:
        text_file = tmp_path / "data.txt"
        text_file.write_text("  first  \nsecond\n", encoding="utf-8")

        assert list(read_line(text_file, strip_line=False)) == ["  first  \n", "second\n"]

    def test_missing_file_raises_os_error_naming_the_file(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "missing.txt"

        with pytest.raises(OSError, match="missing.txt"):
            list(read_line(missing_file))


class TestReadCsvLineHandling:
    def test_blank_lines_are_skipped(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,age\n\nAlice,30\n\n", encoding="utf-8")

        rows = list(read_csv(csv_file))

        assert [row for row, _ in rows] == [{"name": "Alice", "age": "30"}]

    def test_utf8_bom_is_removed_from_first_header(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "data.csv"
        csv_file.write_bytes(codecs.BOM_UTF8 + b"name,age\nAlice,30\n")

        rows = list(read_csv(csv_file))

        assert rows[0][0] == {"name": "Alice", "age": "30"}
        assert rows[0][1].headers == ["name", "age"]


class TestReadCsvAbsoluteLineNumber:
    def test_absolute_line_number_matches_file_line_with_headers(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,age\nAlice,30\nBob,25\nCharlie,40\n")

        rows = list(read_csv(csv_file))

        assert len(rows) == 3
        # Header is line 1, so data starts at line 2
        assert rows[0][1].absolute_line_number == 2
        assert rows[1][1].absolute_line_number == 3
        assert rows[2][1].absolute_line_number == 4

    def test_absolute_line_number_matches_file_line_without_headers(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("Alice,30\nBob,25\nCharlie,40\n")

        rows = list(read_csv(csv_file, has_headers=False))

        assert len(rows) == 3
        assert rows[0][1].absolute_line_number == 1
        assert rows[1][1].absolute_line_number == 2
        assert rows[2][1].absolute_line_number == 3

    def test_data_line_number_is_one_based_data_only_counter(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,age\nAlice,30\nBob,25\n")

        rows = list(read_csv(csv_file))

        assert rows[0][1].data_line_number == 1
        assert rows[1][1].data_line_number == 2

    def test_row_data_parsed_correctly_with_headers(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,age\nAlice,30\nBob,25\n")

        rows = list(read_csv(csv_file))

        assert rows[0][0] == {"name": "Alice", "age": "30"}
        assert rows[1][0] == {"name": "Bob", "age": "25"}

    def test_row_data_parsed_as_list_without_headers(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("Alice,30\nBob,25\n")

        rows = list(read_csv(csv_file, has_headers=False))

        assert rows[0][0] == ["Alice", "30"]
        assert rows[1][0] == ["Bob", "25"]
