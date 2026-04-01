from raccoontools.generators.file_ops_generators import read_csv


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
