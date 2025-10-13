EXT_NAME := ulauncher-fzf
EXT_LOC  := "${HOME}/.local/share/ulauncher/extensions/${EXT_NAME}"
EXT_DIR  := $(shell pwd)

setup:
	uv sync

ci-setup:
	uv sync --frozen

# --- Lint & format ---
lint:
	uv run pre-commit run --all-files

format:
	uv run ruff format .
	uv run ruff check --select I --fix

# --- Tests ---
test:
	uv run pytest

# --- CI targets ---
ci-lint: ci-setup lint
ci-test: ci-setup test

ci: ci-lint ci-test

# --- Dev utilities ---
link:
	if test -h ${EXT_LOC}; then make unlink; fi
	ln -s ${EXT_DIR} ${EXT_LOC}

unlink:
	rm ${EXT_LOC}

start: setup
	ulauncher --dev -v

dev: setup
	ulauncher --no-extensions --dev -v
