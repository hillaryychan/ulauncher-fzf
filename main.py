import logging
import re
import shutil
import subprocess
from enum import Enum
from os import path
from typing import Any, Dict, List, Tuple

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.BaseAction import BaseAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem

logger = logging.getLogger(__name__)


class AltEnterAction(Enum):
    OPEN_PATH = 0
    COPY_PATH = 1


class SearchType(Enum):
    BOTH = 0
    FILES = 1
    DIRS = 2


BinNames = Dict[str, str]
ExtensionPreferences = Dict[str, str]
FuzzyFinderPreferences = Dict[str, Any]


class FuzzyFinderExtension(Extension):
    def __init__(self) -> None:
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    @staticmethod
    def assign_bin_name(bin_names: BinNames, bin_cmd: str, testing_cmd: str) -> BinNames:
        try:
            if shutil.which(testing_cmd):
                bin_names[bin_cmd] = testing_cmd
        except subprocess.CalledProcessError:
            pass

        return bin_names

    @staticmethod
    def check_preferences(preferences: ExtensionPreferences) -> List[str]:
        logger.debug("Checking user preferences are valid")
        errors = []

        base_dir = preferences["base_dir"]
        if not path.isdir(path.expanduser(base_dir)):
            errors.append(f"Base directory '{base_dir}' is not a directory.")

        ignore_file = preferences["ignore_file"]
        if ignore_file and not path.isfile(path.expanduser(ignore_file)):
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
    def get_preferences(input_preferences: ExtensionPreferences) -> FuzzyFinderPreferences:
        preferences: FuzzyFinderPreferences = {
            "alt_enter_action": AltEnterAction(int(input_preferences["alt_enter_action"])),
            "search_type": SearchType(int(input_preferences["search_type"])),
            "allow_hidden": bool(int(input_preferences["allow_hidden"])),
            "follow_symlinks": bool(int(input_preferences["follow_symlinks"])),
            "result_limit": int(input_preferences["result_limit"]),
            "base_dir": path.expanduser(input_preferences["base_dir"]),
            "ignore_file": path.expanduser(input_preferences["ignore_file"]),
            "match_pattern": path.expanduser(input_preferences["match_pattern"]),
            "match_replacement": path.expanduser(input_preferences["match_replacement"]),
        }

        logger.debug("Using user preferences %s", preferences)

        return preferences

    @staticmethod
    def generate_fd_cmd(fd_bin: str, preferences: FuzzyFinderPreferences) -> List[str]:
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

    def get_binaries(self) -> Tuple[BinNames, List[str]]:
        logger.debug("Checking and getting binaries for dependencies")
        bin_names: BinNames = {}
        bin_names = self.assign_bin_name(bin_names, "fzf_bin", "fzf")
        bin_names = self.assign_bin_name(bin_names, "fd_bin", "fd")
        if bin_names.get("fd_bin") is None:
            bin_names = self.assign_bin_name(bin_names, "fd_bin", "fdfind")

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
    ) -> List[str]:
        logger.debug("Finding results for %s", query)

        fd_cmd = self.generate_fd_cmd(fd_bin, preferences)
        with subprocess.Popen(fd_cmd, stdout=subprocess.PIPE) as fd_proc:
            fzf_cmd = [fzf_bin, "--filter", query]
            output = subprocess.check_output(fzf_cmd, stdin=fd_proc.stdout, text=True)
            results = output.splitlines()

            limit = preferences["result_limit"]
            results = results[:limit]
            logger.info("Found results: %s", results)

            return results


class KeywordQueryEventListener(EventListener):
    @staticmethod
    def get_dirname(path_name: str) -> str:
        dirname = path_name if path.isdir(path_name) else path.dirname(path_name)
        return dirname

    @staticmethod
    def no_op_result_items(msgs: List[str], icon: str = "icon") -> RenderResultListAction:
        def create_result_item(msg: str) -> ExtensionResultItem:
            return ExtensionResultItem(
                icon=f"images/{icon}.png",
                name=msg,
                on_enter=DoNothingAction(),
            )

        items = list(map(create_result_item, msgs))
        return RenderResultListAction(items)

    def get_alt_enter_action(self, action_type: AltEnterAction, filename: str) -> BaseAction:
        # Default to opening directory, even if invalid action provided
        action = OpenAction(self.get_dirname(filename))
        if action_type == AltEnterAction.COPY_PATH:
            action = CopyToClipboardAction(filename)
        return action

    def on_event(
        self, event: KeywordQueryEvent, extension: FuzzyFinderExtension
    ) -> RenderResultListAction:
        bin_names, errors = extension.get_binaries()
        errors.extend(extension.check_preferences(extension.preferences))
        if errors:
            return self.no_op_result_items(errors, "error")

        query = event.get_argument()
        if not query:
            return self.no_op_result_items(["Enter your search criteria."])

        preferences = extension.get_preferences(extension.preferences)

        try:
            results = extension.search(query, preferences, **bin_names)
        except subprocess.CalledProcessError as error:
            failing_cmd = error.cmd[0]
            if failing_cmd == "fzf" and error.returncode == 1:
                return self.no_op_result_items(["No results found."])

            logger.debug("Subprocess %s failed with status code %s", error.cmd, error.returncode)
            return self.no_op_result_items(["There was an error running this extension."], "error")

        def create_result_item(path_name: str) -> ExtensionSmallResultItem:
            return ExtensionSmallResultItem(
                icon="images/sub-icon.png",
                name=re.sub(
                    preferences["match_pattern"], preferences["match_replacement"], path_name
                ),
                on_enter=OpenAction(path_name),
                on_alt_enter=self.get_alt_enter_action(preferences["alt_enter_action"], path_name),
            )

        items = list(map(create_result_item, results))
        return RenderResultListAction(items)


if __name__ == "__main__":
    FuzzyFinderExtension().run()
