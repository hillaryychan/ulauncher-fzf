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


def no_op_result_item(msg):
    return RenderResultListAction(
        [
            ExtensionResultItem(
                icon="images/icon.png",
                name=msg,
                on_enter=DoNothingAction(),
            )
        ]
    )


class FuzzyFinderExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def search(self, query):
        logger.info("Finding results for %s", query)

        fd_cmd = ["fd", ".", os.path.expanduser("~")]
        with subprocess.Popen(fd_cmd, stdout=subprocess.PIPE) as fd_proc:
            fzf_cmd = ["fzf", "--filter", query]
            output = subprocess.check_output(fzf_cmd, stdin=fd_proc.stdout, text=True)
            output = output.splitlines()

            results = output[:15]
            logging.info("Found results: %s", results)

            return results


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument()
        if not query or len(query) < 3:
            return no_op_result_item("Keep typing your search criteria ...")

        try:
            results = extension.search(query)

            def create_result_item(filename):
                return ExtensionSmallResultItem(
                    icon="images/icon.png",
                    name=filename,
                    on_enter=OpenAction(filename),
                )

            items = list(map(create_result_item, results))
            return RenderResultListAction(items)
        except subprocess.CalledProcessError as error:
            failing_cmd = error.cmd[0]
            if failing_cmd == "fzf" and error.returncode == 1:
                return no_op_result_item("No results found.")

            logger.debug("Subprocess %s failed with status code %s", error.cmd, error.returncode)
            return no_op_result_item("There was an error running this extension.")


if __name__ == "__main__":
    FuzzyFinderExtension().run()
