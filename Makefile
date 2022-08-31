EXT_NAME := ulauncher-fzf
EXT_LOC  := "${HOME}/.local/share/ulauncher/extensions/${EXT_NAME}"
EXT_DIR  := $(shell pwd)

setup:
	poetry install

lint-run: setup
	poetry run black --check --diff main.py
	poetry run isort --check --diff main.py
	poetry run pylint main.py
	poetry run mypy main.py

lint:
	-make lint-run; \
		status=$$?; \
		exit $$status

format: setup
	poetry run black main.py
	poetry run isort main.py

link:
	if test -h ${EXT_LOC}; then make unlink; fi
	ln -s ${EXT_DIR} ${EXT_LOC}

unlink:
	rm ${EXT_LOC}

start: setup
	ulauncher --dev -v

dev: setup
	ulauncher --no-extensions --dev -v
