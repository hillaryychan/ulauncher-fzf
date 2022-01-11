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
  ln -s {{EXT_DIR}} ~/.local/share/ulauncher/extensions/{{EXT_NAME}}

unlink:
  rm ~/.local/share/ulauncher/extensions/{{EXT_NAME}}

dev:
  ulauncher -v --dev
