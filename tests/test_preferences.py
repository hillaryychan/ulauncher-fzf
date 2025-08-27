from __future__ import annotations

from pathlib import Path, PosixPath
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from src.enums import AltEnterAction, SearchType
from src.preferences import (
    FuzzyFinderPreferences,
    get_preferences,
    validate_preferences,
)

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


class TestGetPreferences:
    @pytest.fixture(autouse=True)
    def mock_path(self, mocker: MockerFixture) -> MagicMock:
        def default_path_side_effect(path_str: str) -> MagicMock:
            path = MagicMock(spec=PosixPath, __str__=MagicMock(return_value=path_str))

            mock_expanduser = MagicMock(spec=Path)
            mock_expanduser.expanduser.return_value = path

            return mock_expanduser

        return mocker.patch(
            "src.preferences.Path", side_effect=default_path_side_effect
        )

    def setup_method(self) -> None:
        self.default_base_dir = "~"
        self.default_result_limit = 15

    def _get_preferences(
        self,
        result_limit: int | None = None,
        base_dir: str | None = None,
        ignore_file: str | None = None,
    ) -> dict[str, Any]:
        return {
            "alt_enter_action": AltEnterAction.OPEN_PATH.value,
            "search_type": SearchType.BOTH.value,
            "allow_hidden": 0,
            "follow_symlinks": 0,
            "trim_display_path": 0,
            "result_limit": result_limit
            if result_limit is not None
            else self.default_result_limit,
            "base_dir": base_dir if base_dir is not None else self.default_base_dir,
            "ignore_file": ignore_file if ignore_file is not None else "",
        }

    def test_get_preferences(self) -> None:
        prefs = self._get_preferences()

        result = get_preferences(prefs)

        assert isinstance(result, FuzzyFinderPreferences)
        assert result.alt_enter_action == AltEnterAction.OPEN_PATH
        assert result.search_type == SearchType.BOTH
        assert result.allow_hidden is False
        assert result.follow_symlinks is False
        assert result.trim_display_path is False
        assert result.result_limit == self.default_result_limit
        assert isinstance(result.base_dir, Path)
        assert str(result.base_dir) == self.default_base_dir
        assert result.ignore_file is None

    def test_empty_base_dir_defaults_to_home(self) -> None:
        prefs = self._get_preferences(base_dir="")

        result = get_preferences(prefs)

        assert isinstance(result, FuzzyFinderPreferences)
        assert result.alt_enter_action == AltEnterAction.OPEN_PATH
        assert result.search_type == SearchType.BOTH
        assert result.allow_hidden is False
        assert result.follow_symlinks is False
        assert result.trim_display_path is False
        assert result.result_limit == self.default_result_limit
        assert isinstance(result.base_dir, Path)
        assert str(result.base_dir) == "~"
        assert result.ignore_file is None

    def test_expands_ignore_file(self) -> None:
        ignore_file = "~/.ulauncherignore"
        prefs = self._get_preferences(ignore_file=ignore_file)

        result = get_preferences(prefs)

        assert isinstance(result, FuzzyFinderPreferences)
        assert result.alt_enter_action == AltEnterAction.OPEN_PATH
        assert result.search_type == SearchType.BOTH
        assert result.allow_hidden is False
        assert result.follow_symlinks is False
        assert result.trim_display_path is False
        assert result.result_limit == self.default_result_limit
        assert isinstance(result.base_dir, Path)
        assert str(result.base_dir) == self.default_base_dir
        assert isinstance(result.ignore_file, Path)
        assert str(result.ignore_file) == ignore_file


class TestValidatePreferences:
    def setup_method(self) -> None:
        self.default_result_limit = 15
        self.base_dir = "~"
        self.mock_base_dir = MagicMock(
            spec=PosixPath, __str__=MagicMock(return_value=self.base_dir)
        )
        self.ignore_file = "~/.ulauncherignore"
        self.mock_ignore_file = MagicMock(
            spec=PosixPath, __str__=MagicMock(return_value=self.ignore_file)
        )

    def _get_preferences(
        self, result_limit: int | None = None
    ) -> FuzzyFinderPreferences:
        return FuzzyFinderPreferences(
            alt_enter_action=AltEnterAction.OPEN_PATH,
            search_type=SearchType.BOTH,
            allow_hidden=False,
            follow_symlinks=False,
            trim_display_path=False,
            result_limit=result_limit if result_limit is not None else 15,
            base_dir=self.mock_base_dir,
            ignore_file=self.mock_ignore_file,
        )

    def test_base_dir_not_is_dir(self) -> None:
        self.mock_base_dir.is_dir.return_value = False

        prefs = self._get_preferences()

        errors = validate_preferences(prefs)

        assert len(errors) == 1
        assert errors[0] == f"Base directory '{self.base_dir}' is not a directory."

    def test_ignore_file_not_is_file(self) -> None:
        self.mock_ignore_file.is_file.return_value = False

        prefs = self._get_preferences()

        errors = validate_preferences(prefs)

        assert len(errors) == 1
        assert errors[0] == f"Ignore file '{self.ignore_file}' is not a file."

    def test_result_limit_lte_0(self) -> None:
        prefs = self._get_preferences(result_limit=0)

        errors = validate_preferences(prefs)

        assert len(errors) == 1
        assert errors[0] == "Result limit must be greater than 0."
