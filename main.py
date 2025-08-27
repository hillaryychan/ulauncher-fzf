from __future__ import annotations

import logging
import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent

from src.commands import get_executable
from src.preferences import get_preferences
from src.results import generate_no_op_result_items, generate_result_items
from src.search import search

logger = logging.getLogger(__name__)


class FuzzyFinderExtension(Extension):
    fzf_cmd: str | None
    fd_cmd: str | None

    def __init__(self) -> None:
        super().__init__()
        self.fzf_cmd = None
        self.fd_cmd = None

        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class PreferencesEventListener(EventListener):
    def on_event(
        self, _event: PreferencesEvent, extension: FuzzyFinderExtension
    ) -> None:
        extension.fzf_cmd = get_executable("fzf")
        extension.fd_cmd = get_executable("fd")
        if extension.fd_cmd is None:
            extension.fd_cmd = get_executable("fdfind")

        logger.debug("Using fzf command: %s", extension.fzf_cmd)
        logger.debug("Using fd command: %s", extension.fd_cmd)


class KeywordQueryEventListener(EventListener):
    def on_event(
        self, event: KeywordQueryEvent, extension: FuzzyFinderExtension
    ) -> RenderResultListAction:
        if extension.fzf_cmd is None or extension.fd_cmd is None:
            errors = []
            if extension.fzf_cmd is None:
                errors.append("Missing dependency fzf. Please install fzf.")
            if extension.fd_cmd is None:
                errors.append("Missing dependency fd. Please install fd.")
            return generate_no_op_result_items(errors, "error")

        preferences, pref_errors = get_preferences(extension.preferences)
        if pref_errors:
            return generate_no_op_result_items(pref_errors, "error")

        logger.debug("Using user preferences %s", preferences)

        query = event.get_argument()
        if not query:
            return generate_no_op_result_items(["Enter your search criteria."])

        try:
            results = search(
                fzf_cmd=extension.fzf_cmd,
                fd_cmd=extension.fd_cmd,
                preferences=preferences,
                query=query,
            )
        except subprocess.CalledProcessError as error:
            failing_cmd = error.cmd[0]
            if failing_cmd == extension.fzf_cmd and error.returncode == 1:
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
