# Ulauncher Fuzzy Finder

Find files and directories in Ulauncher using fzf (and fd).

![ulauncher-fzf preview](https://user-images.githubusercontent.com/44228565/148923401-e8268ef5-974f-4912-8b65-e1704159bfc2.png)

## Requirements

* Ulauncher
* Python 3
* [fzf](https://github.com/junegunn/fzf)
* [fd](https://github.com/sharkdp/fd)

## Features

* Fuzzy searching for files, directories or both
* Allow hidden files to be searched
* Specify preferred number of results returned
* Specify base directory to be searched
* Specify path to ignore-file in '.gitignore' format

Actions:

* Click or press *"Enter"* to open
    * file with default application
    * directory in your file manager
* Press *"Alt+Enter"* to open the directory in which the file is contained.  
    If the path is a directory, this will be the same as pressing Enter

## Development

You can use command runners `make` or [`just`](https://github.com/casey/just) to run project-specific commands. Any `make` target can also be run with `just`. E.g., `make dev` or `just dev`

1. Clone repository

    ```sh
    git clone https://github.com/hillaryychan/ulauncher-fzf.git
    ```

2. (Optional) Install developer dependencies.  
    This is used to install dependencies for running `lint` and `lint-fix`. It will require Python 3.10 and [poetry](https://python-poetry.org/docs/).

    ```sh
    make setup
    ```

3. Create a symlink to the Ulauncher extensions directory

    ```sh
    make link
    ```

4. Stop Ulauncher
5. Run Ulauncher with no extensions and logging enabled

    ```sh
    make dev
    ```

6. In a separate terminal, run ulauncher-fzf.  
    The command to run the extension should be visible in the logging for Step 4. It should look like this:

    ```sh
    VERBOSE=1 ULAUNCHER_WS_API=ws://127.0.0.1:5050/ulauncher-demo PYTHONPATH=/home/username/projects/ulauncher /usr/bin/python /home/username/.local/share/ulauncher/extensions/ulauncher-demo/main.py
    ```

Full list of targets for the command runners:

* `setup` - install developer dependencies
* `lint` - run code linters
* `format-check` - run code formatter checks
* `format` - run code formatters
* `link` - create symlink to Ulauncher extensions directory
* `unlink` - remove symlink created by `link`
* `start` - run Ulauncher with logging enabled
* `dev` - run Ulauncher with no extensions and logging enabled

## Contributing

All contributions are welcome. Raise an issue or open a pull request.

## License

This source code is licensed under the [MIT license](LICENSE).
