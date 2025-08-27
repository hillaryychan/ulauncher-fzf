import logging
import shutil
import subprocess

logger = logging.getLogger(__name__)

BinNames = dict[str, str]


def _assign_bin_name(bin_names: BinNames, bin_cmd: str, testing_cmd: str) -> BinNames:
    try:
        if shutil.which(testing_cmd):
            bin_names[bin_cmd] = testing_cmd
    except subprocess.CalledProcessError:
        pass

    return bin_names


def get_binaries() -> tuple[BinNames, list[str]]:
    logger.debug("Checking and getting binaries for dependencies")
    bin_names: BinNames = {}
    bin_names = _assign_bin_name(bin_names, "fzf_bin", "fzf")
    bin_names = _assign_bin_name(bin_names, "fd_bin", "fd")
    if bin_names.get("fd_bin") is None:
        bin_names = _assign_bin_name(bin_names, "fd_bin", "fdfind")

    errors = []
    if bin_names.get("fzf_bin") is None:
        errors.append("Missing dependency fzf. Please install fzf.")
    if bin_names.get("fd_bin") is None:
        errors.append("Missing dependency fd. Please install fd.")

    if not errors:
        logger.debug("Using binaries %s", bin_names)

    return bin_names, errors
