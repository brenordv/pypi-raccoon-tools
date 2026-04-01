from datetime import datetime, timezone
from unittest.mock import patch

from raccoontools.shared.file_utils import (
    get_date_based_subfolder,
    get_filename_for_new_file,
)


class TestGetFilenameForNewFile:
    def test_basic_json_filename(self):
        filename = get_filename_for_new_file("json")
        assert filename.endswith(".json")
        # Should contain a UUID by default
        assert len(filename) > 10

    def test_extension_with_dot(self):
        filename = get_filename_for_new_file(".csv")
        assert filename.endswith(".csv")
        assert not filename.endswith("..csv")

    def test_extension_without_dot(self):
        filename = get_filename_for_new_file("txt")
        assert filename.endswith(".txt")

    def test_with_prefix(self):
        filename = get_filename_for_new_file("json", prefix="export")
        assert filename.startswith("export-")

    def test_with_suffix(self):
        filename = get_filename_for_new_file("json", suffix="final")
        assert filename.endswith("final.json")

    def test_with_prefix_and_suffix(self):
        filename = get_filename_for_new_file(
            "json", prefix="pre", suffix="suf"
        )
        assert filename.startswith("pre-")
        assert "suf.json" in filename

    def test_no_datetime(self):
        filename = get_filename_for_new_file(
            "json", add_current_datetime_as_format=None
        )
        # Should still have a UUID but no datetime stamp
        parts = filename.replace(".json", "").split("-")
        # UUID4 has 5 parts separated by hyphens
        assert len(parts) >= 5

    def test_no_unique_identifier(self):
        filename = get_filename_for_new_file(
            "json", unique_identifier=False
        )
        # Should not contain a UUID-like pattern
        assert filename.endswith(".json")

    def test_custom_unique_identifier(self):
        """Bug 6 regression: string value for unique_identifier works."""
        filename = get_filename_for_new_file(
            "json", unique_identifier="my-custom-id"
        )
        assert "my-custom-id" in filename

    def test_custom_separator(self):
        filename = get_filename_for_new_file(
            "json",
            prefix="pre",
            suffix="suf",
            part_separator="_",
        )
        assert "_" in filename.replace(".json", "")

    def test_utc_vs_local(self):
        f1 = get_filename_for_new_file("json", use_utc=True)
        f2 = get_filename_for_new_file("json", use_utc=False)
        # Both should produce valid filenames
        assert f1.endswith(".json")
        assert f2.endswith(".json")

    def test_utc_produces_timezone_aware_datetime(self):
        """UTC compat: datetime.now(tz=UTC) must work on all supported Pythons."""
        with patch(
            "raccoontools.shared.file_utils.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = datetime(
                2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc
            )
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

            filename = get_filename_for_new_file(
                "json", use_utc=True, unique_identifier=False
            )
            mock_dt.now.assert_called_once()
            call_kwargs = mock_dt.now.call_args
            assert call_kwargs.kwargs.get("tz") is not None


class TestGetDateBasedSubfolder:
    def test_basic_subfolder_with_fixed_date(self, tmp_path):
        date_ref = datetime(2025, 3, 15, tzinfo=timezone.utc)
        result = get_date_based_subfolder(
            tmp_path, date_ref=date_ref, create_if_missing=False
        )
        assert result == tmp_path / "2025-03-15"

    def test_creates_folder_when_missing(self, tmp_path):
        date_ref = datetime(2025, 1, 1, tzinfo=timezone.utc)
        result = get_date_based_subfolder(
            tmp_path, date_ref=date_ref, create_if_missing=True
        )
        assert result.exists()
        assert result.is_dir()

    def test_does_not_create_folder_when_flag_is_false(self, tmp_path):
        date_ref = datetime(2025, 1, 1, tzinfo=timezone.utc)
        result = get_date_based_subfolder(
            tmp_path, date_ref=date_ref, create_if_missing=False
        )
        assert not result.exists()

    def test_existing_folder_is_not_recreated(self, tmp_path):
        date_ref = datetime(2025, 6, 1, tzinfo=timezone.utc)
        expected = tmp_path / "2025-06-01"
        expected.mkdir()
        marker = expected / "marker.txt"
        marker.write_text("keep")

        result = get_date_based_subfolder(
            tmp_path, date_ref=date_ref, create_if_missing=True
        )
        assert result == expected
        assert marker.read_text() == "keep"

    def test_add_delta_days_positive(self, tmp_path):
        date_ref = datetime(2025, 1, 30, tzinfo=timezone.utc)
        result = get_date_based_subfolder(
            tmp_path, date_ref=date_ref, add_delta_days=3,
            create_if_missing=False
        )
        assert result == tmp_path / "2025-02-02"

    def test_add_delta_days_negative(self, tmp_path):
        date_ref = datetime(2025, 3, 1, tzinfo=timezone.utc)
        result = get_date_based_subfolder(
            tmp_path, date_ref=date_ref, add_delta_days=-1,
            create_if_missing=False
        )
        assert result == tmp_path / "2025-02-28"

    def test_custom_date_format(self, tmp_path):
        date_ref = datetime(2025, 12, 5, tzinfo=timezone.utc)
        result = get_date_based_subfolder(
            tmp_path, date_ref=date_ref, date_format="%Y/%m/%d",
            create_if_missing=False
        )
        assert result == tmp_path / "2025" / "12" / "05"

    def test_ref_path_is_file_uses_parent(self, tmp_path):
        file_path = tmp_path / "some_file.txt"
        file_path.write_text("data")
        date_ref = datetime(2025, 7, 4, tzinfo=timezone.utc)

        result = get_date_based_subfolder(
            file_path, date_ref=date_ref, create_if_missing=False
        )
        assert result == tmp_path / "2025-07-04"

    def test_nonexistent_path_with_extension_uses_parent(self, tmp_path):
        fake_file = tmp_path / "output" / "report.json"
        date_ref = datetime(2025, 7, 4, tzinfo=timezone.utc)

        result = get_date_based_subfolder(
            fake_file, date_ref=date_ref, create_if_missing=False
        )
        assert result == tmp_path / "output" / "2025-07-04"

    def test_nonexistent_path_without_extension_treated_as_dir(self, tmp_path):
        fake_dir = tmp_path / "output" / "reports"
        date_ref = datetime(2025, 7, 4, tzinfo=timezone.utc)

        result = get_date_based_subfolder(
            fake_dir, date_ref=date_ref, create_if_missing=False
        )
        assert result == fake_dir / "2025-07-04"

    def test_use_utc_true_calls_now_with_tz(self, tmp_path):
        with patch(
            "raccoontools.shared.file_utils.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = datetime(
                2025, 1, 1, tzinfo=timezone.utc
            )
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

            get_date_based_subfolder(
                tmp_path, use_utc=True, create_if_missing=False
            )
            mock_dt.now.assert_called_once()
            assert mock_dt.now.call_args.kwargs.get("tz") is not None

    def test_use_utc_false_calls_now_without_tz(self, tmp_path):
        with patch(
            "raccoontools.shared.file_utils.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)

            get_date_based_subfolder(
                tmp_path, use_utc=False, create_if_missing=False
            )
            mock_dt.now.assert_called_once()
            assert mock_dt.now.call_args.kwargs.get("tz") is None

    def test_creates_nested_parents(self, tmp_path):
        base = tmp_path / "a" / "b" / "c"
        date_ref = datetime(2025, 1, 1, tzinfo=timezone.utc)
        result = get_date_based_subfolder(
            base, date_ref=date_ref, create_if_missing=True
        )
        assert result.exists()
        assert result == base / "2025-01-01"
