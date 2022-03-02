import logging
import shutil
import subprocess
from enum import Enum
from os import path
from typing import Dict

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem

logger = logging.getLogger(__name__)

BinNames = Dict[str, str]
ExtensionPreferences = Dict[str, str]


class SearchType(Enum):
    BOTH = 0
    FILES = 1
    DIRS = 2


def get_dirname(filename: str) -> str:
    dirname = filename if path.isdir(filename) else path.dirname(filename)
    return dirname


def no_op_result_items(msgs: list[str], icon: str = "icon") -> RenderResultListAction:
    def create_result_item(msg):
        return ExtensionResultItem(
            icon=f"images/{icon}.png",
            name=msg,
            on_enter=DoNothingAction(),
        )

    items = list(map(create_result_item, msgs))
    return RenderResultListAction(items)


class FuzzyFinderExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def assign_bin_name(self, bin_names: BinNames, bin_cmd: str, testing_cmd: str) -> BinNames:
        try:
            if shutil.which(testing_cmd):
                bin_names[bin_cmd] = testing_cmd
        except subprocess.CalledProcessError:
            pass

        return bin_names

    def get_binaries(self) -> tuple[BinNames, list[str]]:
        logger.debug("Checking and getting binaries for dependencies")
        bin_names = {}
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

    def check_preferences(self, preferences: ExtensionPreferences) -> list[str]:
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

    def get_preferences(self, input_preferences: ExtensionPreferences) -> ExtensionPreferences:
        preferences = {}
        preferences["search_type"] = SearchType(int(input_preferences["search_type"]))
        preferences["allow_hidden"] = bool(int(input_preferences["allow_hidden"]))
        preferences["result_limit"] = int(input_preferences["result_limit"])
        preferences["base_dir"] = path.expanduser(input_preferences["base_dir"])
        preferences["ignore_file"] = path.expanduser(input_preferences["ignore_file"])

        logger.debug("Using user preferences %s", preferences)

        return preferences

    def generate_fd_cmd(self, fd_bin: str, preferences: ExtensionPreferences) -> list[str]:
        cmd = [fd_bin, ".", preferences["base_dir"]]
        if preferences["search_type"] == SearchType.FILES:
            cmd.extend(["--type", "f"])
        elif preferences["search_type"] == SearchType.DIRS:
            cmd.extend(["--type", "d"])

        if preferences["allow_hidden"]:
            cmd.extend(["--hidden"])

        if preferences["ignore_file"]:
            cmd.extend(["--ignore-file", preferences["ignore_file"]])

        return cmd

    def search(
        self, query: str, preferences: ExtensionPreferences, fd_bin: str, fzf_bin: str
    ) -> list[str]:
        logger.debug("Finding results for %s", query)

        fd_cmd = self.generate_fd_cmd(fd_bin, preferences)
        with subprocess.Popen(fd_cmd, stdout=subprocess.PIPE) as fd_proc:
            fzf_cmd = [fzf_bin, "--filter", query]
            output = subprocess.check_output(fzf_cmd, stdin=fd_proc.stdout, text=True)
            output = output.splitlines()

            limit = preferences["result_limit"]
            results = output[:limit]
            logger.info("Found results: %s", results)

            return results


class KeywordQueryEventListener(EventListener):
    def on_event(
        self, event: KeywordQueryEvent, extension: FuzzyFinderExtension
    ) -> RenderResultListAction:
        bin_names, errors = extension.get_binaries()
        errors.extend(extension.check_preferences(extension.preferences))
        if errors:
            return no_op_result_items(errors, "error")

        query = event.get_argument()
        if not query:
            return no_op_result_items(["Enter your search criteria."])

        try:
            preferences = extension.get_preferences(extension.preferences)
            results = extension.search(query, preferences, **bin_names)

            def create_result_item(filename):
                return ExtensionSmallResultItem(
                    icon="images/sub-icon.png",
                    name=filename,
                    on_enter=OpenAction(filename),
                    on_alt_enter=OpenAction(get_dirname(filename)),
                )

            items = list(map(create_result_item, results))
            return RenderResultListAction(items)
        except subprocess.CalledProcessError as error:
            failing_cmd = error.cmd[0]
            if failing_cmd == "fzf" and error.returncode == 1:
                return no_op_result_items(["No results found."])

            logger.debug("Subprocess %s failed with status code %s", error.cmd, error.returncode)
            return no_op_result_items(["There was an error running this extension."], "error")


if __name__ == "__main__":
    FuzzyFinderExtension().run()
