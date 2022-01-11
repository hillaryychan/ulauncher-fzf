import logging
import os
import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem

logger = logging.getLogger(__name__)


def no_op_result_items(msgs):
    def create_result_item(msg):
        return ExtensionResultItem(
            icon="images/icon.png",
            name=msg,
            on_enter=DoNothingAction(),
        )

    items = list(map(create_result_item, msgs))
    return RenderResultListAction(items)


class FuzzyFinderExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def assign_bin_name(self, bin_names, bin_cmd, testing_cmd):
        try:
            subprocess.check_call(["command", "-v", testing_cmd])
            bin_names[bin_cmd] = testing_cmd
        except subprocess.CalledProcessError:
            pass

        return bin_names

    def check_dependencies(self):
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
        if len(errors) == 0:
            errors = None

        return bin_names, errors

    def search(self, query, fd_bin, fzf_bin):
        logger.info("Finding results for %s", query)

        fd_cmd = [fd_bin, ".", os.path.expanduser("~")]
        with subprocess.Popen(fd_cmd, stdout=subprocess.PIPE) as fd_proc:
            fzf_cmd = [fzf_bin, "--filter", query]
            output = subprocess.check_output(fzf_cmd, stdin=fd_proc.stdout, text=True)
            output = output.splitlines()

            results = output[:15]
            logging.info("Found results: %s", results)

            return results


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        bin_names, errors = extension.check_dependencies()
        if errors:
            return no_op_result_items(errors)

        query = event.get_argument()
        if not query:
            return no_op_result_items(["Enter your search criteria."])

        try:
            results = extension.search(query, **bin_names)

            def create_result_item(filename):
                return ExtensionSmallResultItem(
                    icon="images/sub-icon.png",
                    name=filename,
                    on_enter=OpenAction(filename),
                )

            items = list(map(create_result_item, results))
            return RenderResultListAction(items)
        except subprocess.CalledProcessError as error:
            failing_cmd = error.cmd[0]
            if failing_cmd == "fzf" and error.returncode == 1:
                return no_op_result_items(["No results found."])

            logger.debug("Subprocess %s failed with status code %s", error.cmd, error.returncode)
            return no_op_result_items(["There was an error running this extension."])


if __name__ == "__main__":
    FuzzyFinderExtension().run()
