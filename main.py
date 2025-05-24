from __future__ import annotations

import logging
import shutil
import subprocess
from enum import Enum
from os import path
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem

if TYPE_CHECKING:
    from ulauncher.api.shared.action.BaseAction import BaseAction

logger = logging.getLogger(__name__)


class AltEnterAction(Enum):
    OPEN_PATH = 0
    COPY_PATH = 1


class SearchType(Enum):
    BOTH = 0
    FILES = 1
    DIRS = 2


BinNames = dict[str, str]
ExtensionPreferences = dict[str, str]
FuzzyFinderPreferences = dict[str, Any]


class FuzzyFinderExtension(Extension):
    def __init__(self) -> None:
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    @staticmethod
    def _assign_bin_name(
        bin_names: BinNames, bin_cmd: str, testing_cmd: str
    ) -> BinNames:
        try:
            if shutil.which(testing_cmd):
                bin_names[bin_cmd] = testing_cmd
        except subprocess.CalledProcessError:
            pass

        return bin_names

    @staticmethod
    def _validate_preferences(preferences: ExtensionPreferences) -> list[str]:
        logger.debug("Validating user preferences")
        errors = []

        base_dir = preferences["base_dir"]
        if not Path(Path(base_dir).expanduser()).is_dir():
            errors.append(f"Base directory '{base_dir}' is not a directory.")

        ignore_file = preferences["ignore_file"]
        if ignore_file and not Path(Path(ignore_file).expanduser()).is_file():
            errors.append(f"Ignore file '{ignore_file}' is not a file.")

        try:
            result_limit = int(preferences["result_limit"])
            if result_limit <= 0:
                errors.append("Result limit must be greater than 0.")
        except ValueError:
            errors.append("Result limit must be an integer.")

        if not errors:
            logger.debug("User preferences validated")

        return errors

    @staticmethod
    def get_preferences(
        input_preferences: ExtensionPreferences,
    ) -> tuple[FuzzyFinderPreferences, list[str]]:
        preferences: FuzzyFinderPreferences = {
            "alt_enter_action": AltEnterAction(
                int(input_preferences["alt_enter_action"])
            ),
            "search_type": SearchType(int(input_preferences["search_type"])),
            "allow_hidden": bool(int(input_preferences["allow_hidden"])),
            "follow_symlinks": bool(int(input_preferences["follow_symlinks"])),
            "trim_display_path": bool(int(input_preferences["trim_display_path"])),
            "result_limit": int(input_preferences["result_limit"]),
            "base_dir": str(Path(input_preferences["base_dir"]).expanduser()),
            "ignore_file": str(Path(input_preferences["ignore_file"]).expanduser()),
        }

        errors = FuzzyFinderExtension._validate_preferences(preferences)

        return preferences, errors

    @staticmethod
    def _generate_fd_cmd(fd_bin: str, preferences: FuzzyFinderPreferences) -> list[str]:
        cmd = [fd_bin, ".", preferences["base_dir"]]
        if preferences["search_type"] == SearchType.FILES:
            cmd.extend(["--type", "f"])
        elif preferences["search_type"] == SearchType.DIRS:
            cmd.extend(["--type", "d"])

        if preferences["allow_hidden"]:
            cmd.extend(["--hidden"])

        if preferences["follow_symlinks"]:
            cmd.extend(["--follow"])

        if preferences["ignore_file"]:
            cmd.extend(["--ignore-file", preferences["ignore_file"]])

        return cmd

    def get_binaries(self) -> tuple[BinNames, list[str]]:
        logger.debug("Checking and getting binaries for dependencies")
        bin_names: BinNames = {}
        bin_names = FuzzyFinderExtension._assign_bin_name(bin_names, "fzf_bin", "fzf")
        bin_names = FuzzyFinderExtension._assign_bin_name(bin_names, "fd_bin", "fd")
        if bin_names.get("fd_bin") is None:
            bin_names = FuzzyFinderExtension._assign_bin_name(
                bin_names, "fd_bin", "fdfind"
            )

        errors = []
        if bin_names.get("fzf_bin") is None:
            errors.append("Missing dependency fzf. Please install fzf.")
        if bin_names.get("fd_bin") is None:
            errors.append("Missing dependency fd. Please install fd.")

        if not errors:
            logger.debug("Using binaries %s", bin_names)

        return bin_names, errors

    def search(
        self, query: str, preferences: FuzzyFinderPreferences, fd_bin: str, fzf_bin: str
    ) -> list[str]:
        logger.debug("Finding results for %s", query)

        fd_cmd = FuzzyFinderExtension._generate_fd_cmd(fd_bin, preferences)
        with subprocess.Popen(fd_cmd, stdout=subprocess.PIPE) as fd_proc:  # noqa: S603
            fzf_cmd = [fzf_bin, "--filter", query]
            output = subprocess.check_output(fzf_cmd, stdin=fd_proc.stdout, text=True)  # noqa: S603
            results = output.splitlines()

            limit = preferences["result_limit"]
            results = results[:limit]
            logger.info("Found results: %s", results)

            return results


class KeywordQueryEventListener(EventListener):
    @staticmethod
    def _get_dirname(path_name: str) -> str:
        return path_name if Path(path_name).is_dir() else str(Path(path_name).parent)

    @staticmethod
    def _no_op_result_items(
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

    @staticmethod
    def _get_alt_enter_action(action_type: AltEnterAction, filename: str) -> BaseAction:
        # Default to opening directory, even if invalid action provided
        action = OpenAction(KeywordQueryEventListener._get_dirname(filename))
        if action_type == AltEnterAction.COPY_PATH:
            action = CopyToClipboardAction(filename)
        return action

    @staticmethod
    def _get_path_prefix(results: list[str], trim_path: bool) -> str | None:  # noqa: FBT001
        path_prefix = None
        if trim_path:
            common_path = path.commonpath(results)
            common_path_parent = str(Path(common_path).parent)
            if common_path_parent not in ("/", ""):
                path_prefix = common_path_parent

        logger.debug("path_prefix for results is '%s'", path_prefix or "")

        return path_prefix

    @staticmethod
    def _get_display_name(path_name: str, path_prefix: str | None = None) -> str:
        display_path = path_name
        if path_prefix is not None:
            display_path = path_name.replace(path_prefix, "...")
        return display_path

    @staticmethod
    def _generate_result_items(
        preferences: FuzzyFinderPreferences, results: list[str]
    ) -> list[ExtensionSmallResultItem]:
        path_prefix = KeywordQueryEventListener._get_path_prefix(
            results, preferences["trim_display_path"]
        )

        def create_result_item(path_name: str) -> ExtensionSmallResultItem:
            return ExtensionSmallResultItem(
                icon="images/sub-icon.png",
                name=KeywordQueryEventListener._get_display_name(
                    path_name, path_prefix
                ),
                on_enter=OpenAction(path_name),
                on_alt_enter=KeywordQueryEventListener._get_alt_enter_action(
                    preferences["alt_enter_action"], path_name
                ),
            )

        return list(map(create_result_item, results))

    def on_event(
        self, event: KeywordQueryEvent, extension: FuzzyFinderExtension
    ) -> RenderResultListAction:
        bin_names, bin_errors = extension.get_binaries()
        preferences, pref_errors = extension.get_preferences(extension.preferences)
        errors = bin_errors + pref_errors
        if errors:
            return KeywordQueryEventListener._no_op_result_items(errors, "error")

        logger.debug("Using user preferences %s", preferences)

        query = event.get_argument()
        if not query:
            return KeywordQueryEventListener._no_op_result_items(
                ["Enter your search criteria."]
            )

        try:
            results = extension.search(query, preferences, **bin_names)
        except subprocess.CalledProcessError as error:
            failing_cmd = error.cmd[0]
            if failing_cmd == "fzf" and error.returncode == 1:
                return KeywordQueryEventListener._no_op_result_items(
                    ["No results found."]
                )

            logger.debug(
                "Subprocess %s failed with status code %s", error.cmd, error.returncode
            )
            return KeywordQueryEventListener._no_op_result_items(
                ["There was an error running this extension."], "error"
            )

        items = KeywordQueryEventListener._generate_result_items(preferences, results)

        return RenderResultListAction(items)


if __name__ == "__main__":
    FuzzyFinderExtension().run()
