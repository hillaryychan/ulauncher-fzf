EXT_NAME := "ulauncher-fzf"
EXT_LOC  := "~/.local/share/ulauncher/extensions/" + EXT_NAME
EXT_DIR  := justfile_directory()

# List available recipes
default:
  @just --list

# Install dependencies
setup:
  poetry install

# Run code linters and formatters
lint: setup
  #!/usr/bin/env bash
  status=0
  poetry run ruff check main.py
  poetry run ruff format --check --diff main.py
  poetry run mypy main.py || status=$?
  exit $status

# Run code formatters and import organisers
format: setup
  poetry run ruff format main.py
  poetry run ruff check --select I --fix

# Create symbolic link to Ulauncher's extension directory
link:
  if test -h {{EXT_LOC}}; then just unlink; fi
  ln -s {{EXT_DIR}} {{EXT_LOC}}

# Remove symbolic link to Ulauncher's extension directory
unlink:
  rm {{EXT_LOC}}

# Start Ulauncher in developer and verbose mode
start: setup
  ulauncher --dev -v

# Start Ulauncher in developer and verbose mode with no extensions enabled
dev: setup
  ulauncher --no-extensions --dev -v
