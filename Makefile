EXT_NAME := ulauncher-fzf
EXT_LOC  := "${HOME}/.local/share/ulauncher/extensions/${EXT_NAME}"
EXT_DIR  := $(shell pwd)

setup:
	uv sync

lint-run: setup
	uv run black --check --diff main.py
	uv run isort --check --diff main.py
	uv run pylint main.py
	uv run mypy main.py

lint:
	-make lint-run; \
		status=$$?; \
		exit $$status

format: setup
	uv run black main.py
	uv run isort main.py

link:
	if test -h ${EXT_LOC}; then make unlink; fi
	ln -s ${EXT_DIR} ${EXT_LOC}

unlink:
	rm ${EXT_LOC}

start: setup
	ulauncher --dev -v

dev: setup
	ulauncher --no-extensions --dev -v
