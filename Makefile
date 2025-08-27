EXT_NAME := ulauncher-fzf
EXT_LOC  := "${HOME}/.local/share/ulauncher/extensions/${EXT_NAME}"
EXT_DIR  := $(shell pwd)

setup:
	uv sync

lint-run: setup
	uv run ruff check .
	uv run ruff format --check --diff .
	uv run mypy .

lint:
	-make lint-run; \
		status=$$?; \
		exit $$status

format: setup
	uv run ruff format .
	uv run ruff check --select I --fix

link:
	if test -h ${EXT_LOC}; then make unlink; fi
	ln -s ${EXT_DIR} ${EXT_LOC}

unlink:
	rm ${EXT_LOC}

start: setup
	ulauncher --dev -v

dev: setup
	ulauncher --no-extensions --dev -v
