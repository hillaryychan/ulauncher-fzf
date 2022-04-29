EXT_NAME := ulauncher-fzf
EXT_LOC  := "${HOME}/.local/share/ulauncher/extensions/${EXT_NAME}"
EXT_DIR  := $(shell pwd)

setup:
	poetry install

lint:
	poetry run flake8 main.py
	poetry run pylint main.py
	poetry run mypy main.py

format-check:
	poetry run black --check --diff main.py
	poetry run isort --check --diff main.py

format:
	poetry run black main.py
	poetry run isort main.py

link:
	if test -h ${EXT_LOC}; then make unlink; fi
	ln -s ${EXT_DIR} ${EXT_LOC}

unlink:
	rm ${EXT_LOC}

start:
	ulauncher --dev -v

dev:
	ulauncher --no-extensions --dev -v
