import subprocess
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from src.commands import get_executable


class TestGetExecutable:
    @pytest.fixture(autouse=True)
    def mock_shutil(self, mocker: MockerFixture) -> MagicMock:
        return mocker.patch("src.commands.shutil")

    def test_get_executable(self, mock_shutil: MagicMock) -> None:
        executable = "/usr/bin/cmd"
        mock_shutil.which.return_value = executable
        assert get_executable("cmd") == executable

    def test_get_executable_on(self, mock_shutil: MagicMock) -> None:
        mock_shutil.which.side_effect = subprocess.CalledProcessError(1, "cmd")
        assert get_executable("cmd") is None
