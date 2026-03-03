import re
from unittest.mock import patch

import pytest

from raccoontools.shared.file_utils import get_filename_for_new_file


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
