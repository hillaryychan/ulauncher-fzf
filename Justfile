EXT_NAME := "ulauncher-fzf"
EXT_LOC  := "~/.local/share/ulauncher/extensions/" + EXT_NAME
EXT_DIR  := justfile_directory()

setup:
  poetry install

lint:
  poetry run flake8 main.py
  poetry run pylint main.py

lint-fix:
  poetry run black main.py
  poetry run isort main.py

link:
  if test -h {{EXT_LOC}}; then just unlink; fi
  ln -s {{EXT_DIR}} {{EXT_LOC}}

unlink:
  rm {{EXT_LOC}}

start:
  ulauncher --dev -v

dev:
  ulauncher --no-extensions --dev -v
