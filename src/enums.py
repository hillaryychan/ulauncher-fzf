from enum import Enum


class AltEnterAction(Enum):
    OPEN_PATH = 0
    COPY_PATH = 1


class SearchType(Enum):
    BOTH = 0
    FILES = 1
    DIRS = 2
