from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from src.enums import AltEnterAction, SearchType

logger = logging.getLogger(__name__)


@dataclass
class FuzzyFinderPreferences:
    alt_enter_action: AltEnterAction
    search_type: SearchType
    allow_hidden: bool
    follow_symlinks: bool
    trim_display_path: bool
    result_limit: int
    base_dir: Path
    ignore_file: Path | None


def _expand_path(path: str) -> Path | None:
    return Path(path).expanduser() if path else None


def _validate_preferences(preferences: FuzzyFinderPreferences) -> list[str]:
    logger.debug("Validating user preferences")
    errors = []

    base_dir = preferences.base_dir
    if not base_dir.is_dir():
        errors.append(f"Base directory '{base_dir}' is not a directory.")

    ignore_file = preferences.ignore_file
    if ignore_file and not ignore_file.is_file():
        errors.append(f"Ignore file '{ignore_file}' is not a file.")

    try:
        result_limit = preferences.result_limit
        if result_limit <= 0:
            errors.append("Result limit must be greater than 0.")
    except ValueError:
        errors.append("Result limit must be an integer.")

    if not errors:
        logger.debug("User preferences validated")

    return errors


def get_preferences(
    input_preferences: dict[str, str],
) -> tuple[FuzzyFinderPreferences, list[str]]:
    preferences = FuzzyFinderPreferences(
        alt_enter_action=AltEnterAction(int(input_preferences["alt_enter_action"])),
        search_type=SearchType(int(input_preferences["search_type"])),
        allow_hidden=bool(int(input_preferences["allow_hidden"])),
        follow_symlinks=bool(int(input_preferences["follow_symlinks"])),
        trim_display_path=bool(int(input_preferences["trim_display_path"])),
        result_limit=int(input_preferences["result_limit"]),
        base_dir=_expand_path(input_preferences["base_dir"]) or Path("~").expanduser(),
        ignore_file=_expand_path(input_preferences["ignore_file"]),
    )

    errors = _validate_preferences(preferences)

    return preferences, errors
