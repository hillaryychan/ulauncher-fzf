from __future__ import annotations

import logging
import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent

from src.binaries import get_binaries
from src.preferences import get_preferences
from src.results import generate_no_op_result_items, generate_result_items
from src.search import search

logger = logging.getLogger(__name__)


class FuzzyFinderExtension(Extension):
    def __init__(self) -> None:
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(
        self, event: KeywordQueryEvent, extension: FuzzyFinderExtension
    ) -> RenderResultListAction:
        bin_names, bin_errors = get_binaries()
        preferences, pref_errors = get_preferences(extension.preferences)
        errors = bin_errors + pref_errors
        if errors:
            return generate_no_op_result_items(errors, "error")

        logger.debug("Using user preferences %s", preferences)

        query = event.get_argument()
        if not query:
            return generate_no_op_result_items(["Enter your search criteria."])

        try:
            results = search(query, preferences, **bin_names)
        except subprocess.CalledProcessError as error:
            failing_cmd = error.cmd[0]
            if failing_cmd == "fzf" and error.returncode == 1:
                return generate_no_op_result_items(["No results found."])

            logger.debug(
                "Subprocess %s failed with status code %s", error.cmd, error.returncode
            )
            return generate_no_op_result_items(
                ["There was an error running this extension."], "error"
            )
        items = generate_result_items(preferences, results)
        return RenderResultListAction(items)


if __name__ == "__main__":
    FuzzyFinderExtension().run()
