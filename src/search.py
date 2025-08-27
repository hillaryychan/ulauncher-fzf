import logging
import subprocess

from src.enums import SearchType
from src.preferences import FuzzyFinderPreferences

logger = logging.getLogger(__name__)


def _generate_fd_cmd(fd_bin: str, preferences: FuzzyFinderPreferences) -> list[str]:
    cmd: list[str] = [fd_bin, ".", str(preferences.base_dir)]
    if preferences.search_type == SearchType.FILES:
        cmd.extend(["--type", "f"])
    elif preferences.search_type == SearchType.DIRS:
        cmd.extend(["--type", "d"])

    if preferences.allow_hidden:
        cmd.extend(["--hidden"])

    if preferences.follow_symlinks:
        cmd.extend(["--follow"])

    if preferences.ignore_file:
        cmd.extend(["--ignore-file", str(preferences.ignore_file)])

    return cmd


def search(
    query: str, preferences: FuzzyFinderPreferences, fd_bin: str, fzf_bin: str
) -> list[str]:
    logger.debug("Finding results for %s", query)

    fd_cmd = _generate_fd_cmd(fd_bin, preferences)
    with subprocess.Popen(fd_cmd, stdout=subprocess.PIPE) as fd_proc:  # noqa: S603
        fzf_cmd = [fzf_bin, "--filter", query]
        output = subprocess.check_output(fzf_cmd, stdin=fd_proc.stdout, text=True)  # noqa: S603
        results = output.splitlines()

        limit = preferences.result_limit
        results = results[:limit]
        logger.info("Found results: %s", results)

        return results
