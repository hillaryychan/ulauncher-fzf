from __future__ import annotations

import logging
from os import path
from pathlib import Path
from typing import TYPE_CHECKING

from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem

from src.enums import AltEnterAction

if TYPE_CHECKING:
    from ulauncher.api.shared.action.BaseAction import BaseAction

    from src.preferences import FuzzyFinderPreferences

logger = logging.getLogger(__name__)


def _get_dirname(path_name: str) -> str:
    return path_name if Path(path_name).is_dir() else str(Path(path_name).parent)


def _get_alt_enter_action(action_type: AltEnterAction, filename: str) -> BaseAction:
    # Default to opening directory, even if invalid action provided
    action = OpenAction(_get_dirname(filename))
    if action_type == AltEnterAction.COPY_PATH:
        action = CopyToClipboardAction(filename)
    return action


def _get_path_prefix(results: list[str], trim_path: bool) -> str | None:  # noqa: FBT001
    path_prefix = None
    if trim_path:
        common_path = path.commonpath(results)
        common_path_parent = str(Path(common_path).parent)
        if common_path_parent not in ("/", ""):
            path_prefix = common_path_parent

    logger.debug("path_prefix for results is '%s'", path_prefix or "")

    return path_prefix


def _get_display_name(path_name: str, path_prefix: str | None = None) -> str:
    display_path = path_name
    if path_prefix is not None:
        display_path = path_name.replace(path_prefix, "...")
    return display_path


def generate_result_items(
    preferences: FuzzyFinderPreferences, results: list[str]
) -> list[ExtensionSmallResultItem]:
    path_prefix = _get_path_prefix(results, preferences.trim_display_path)

    def create_result_item(path_name: str) -> ExtensionSmallResultItem:
        return ExtensionSmallResultItem(
            icon="images/sub-icon.png",
            name=_get_display_name(path_name, path_prefix),
            on_enter=OpenAction(path_name),
            on_alt_enter=_get_alt_enter_action(preferences.alt_enter_action, path_name),
        )

    return list(map(create_result_item, results))


def generate_no_op_result_items(
    msgs: list[str], icon: str = "icon"
) -> RenderResultListAction:
    def create_result_item(msg: str) -> ExtensionResultItem:
        return ExtensionResultItem(
            icon=f"images/{icon}.png",
            name=msg,
            on_enter=DoNothingAction(),
        )

    items = list(map(create_result_item, msgs))
    return RenderResultListAction(items)
