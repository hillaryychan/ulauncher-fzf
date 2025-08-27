import subprocess
from unittest.mock import MagicMock, call

import pytest
from pytest_mock.plugin import MockerFixture

from src.binaries import get_binaries


class TestGetBinaries:
    @pytest.fixture(autouse=True)
    def mock_shutil(self, mocker: MockerFixture) -> MagicMock:
        return mocker.patch("src.binaries.shutil")

    def test_get_binaries(self, mock_shutil: MagicMock) -> None:
        mock_shutil.which.return_value = "cmd"
        bin_names, errors = get_binaries()

        assert errors == []

        assert isinstance(bin_names, dict)
        assert bin_names["fzf_bin"] == "fzf"
        assert bin_names["fd_bin"] == "fd"

        assert mock_shutil.which.call_count == 2
        mock_shutil.which.assert_has_calls(
            [
                call("fzf"),
                call("fd"),
            ]
        )

    def test_get_binaries_uses_fdfind_when_no_fd(self, mock_shutil: MagicMock) -> None:
        mock_shutil.which.side_effect = ["fzf", subprocess.CalledProcessError(1, "fzf"), "fdfind"]
        bin_names, errors = get_binaries()

        assert errors == []

        assert isinstance(bin_names, dict)
        assert bin_names["fzf_bin"] == "fzf"
        assert bin_names["fd_bin"] == "fdfind"

        assert mock_shutil.which.call_count == 3
        mock_shutil.which.assert_has_calls(
            [
                call("fzf"),
                call("fd"),
                call("fdfind"),
            ]
        )

    def test_missing_fzf(self, mock_shutil: MagicMock) -> None:
        mock_shutil.which.side_effect = [subprocess.CalledProcessError(1, "fzf"), "fd"]
        _, errors = get_binaries()

        assert len(errors) == 1
        assert errors[0] == "Missing dependency fzf. Please install fzf."

        assert mock_shutil.which.call_count == 2
        mock_shutil.which.assert_has_calls(
            [
                call("fzf"),
                call("fd"),
            ]
        )

    def test_missing_fd(self, mock_shutil: MagicMock) -> None:
        mock_shutil.which.side_effect = [
            "fzf",
            subprocess.CalledProcessError(1, "fd"),
            subprocess.CalledProcessError(1, "fdfind"),
        ]
        _, errors = get_binaries()

        assert len(errors) == 1
        assert errors[0] == "Missing dependency fd. Please install fd."

        assert mock_shutil.which.call_count == 3
        mock_shutil.which.assert_has_calls(
            [
                call("fzf"),
                call("fd"),
                call("fdfind"),
            ]
        )
