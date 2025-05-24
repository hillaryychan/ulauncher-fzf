EXT_NAME := ulauncher-fzf
EXT_LOC  := "${HOME}/.local/share/ulauncher/extensions/${EXT_NAME}"
EXT_DIR  := $(shell pwd)

setup:
	poetry install

lint-run: setup
	poetry run ruff check main.py
	poetry run ruff format --check --diff main.py
	poetry run mypy main.py

lint:
	-make lint-run; \
		status=$$?; \
		exit $$status

format: setup
	poetry run ruff format main.py
	poetry run ruff check --select I --fix

link:
	if test -h ${EXT_LOC}; then make unlink; fi
	ln -s ${EXT_DIR} ${EXT_LOC}

unlink:
	rm ${EXT_LOC}

start: setup
	ulauncher --dev -v

dev: setup
	ulauncher --no-extensions --dev -v
