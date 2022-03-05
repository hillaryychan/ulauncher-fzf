EXT_NAME := "ulauncher-fzf"
EXT_LOC  := "~/.local/share/ulauncher/extensions/" + EXT_NAME
EXT_DIR  := justfile_directory()

# List available recipes
default:
  @just --list

# Install dependencies
setup:
  poetry install

# Run code linters
lint:
  poetry run flake8 main.py
  poetry run pylint main.py
  poetry run mypy main.py

# Run code formatters and import organisers
lint-fix:
  poetry run black main.py
  poetry run isort main.py

# Create symbolic link to Ulauncher's extension directory
link:
  if test -h {{EXT_LOC}}; then just unlink; fi
  ln -s {{EXT_DIR}} {{EXT_LOC}}

# Remove symbolic link to Ulauncher's extension directory
unlink:
  rm {{EXT_LOC}}

# Start Ulauncher in developer and verbose mode
start:
  ulauncher --dev -v

# Start Ulauncher in developer and verbose mode with no extensions enabled
dev:
  ulauncher --no-extensions --dev -v
