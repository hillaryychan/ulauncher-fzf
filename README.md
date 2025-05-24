# Ulauncher Fuzzy Finder

Find files and directories in Ulauncher using fzf (and fd).

![ulauncher-fzf preview](https://user-images.githubusercontent.com/44228565/148923401-e8268ef5-974f-4912-8b65-e1704159bfc2.png)

## Requirements

* Ulauncher
* Python 3.9 or higher
* [fzf](https://github.com/junegunn/fzf)
* [fd](https://github.com/sharkdp/fd)

## Features

* Fuzzy searching for files, directories or both
* Allow hidden files to be searched
* Follow symbolic links
* Specify preferred number of results returned
* Specify base directory to be searched
* Ignore certain files and directories - you can do this by creating an ignore-file
which follows the [`.gitignore`](https://git-scm.com/docs/gitignore#_pattern_format)
format, then specify the path to ignore-file in the extension's settings.

Actions:

* Click or press *"Enter"* to open
    * a file with its default application
    * a directory in your file manager
* You can select your preferred action for *"Alt+Enter"*. Actions include:
    * opening the directory in which the file is contained (default)
    * copying the file path to your clipboard

## Development

You can use command runners `make` to run project-specific commands. E.g., `make dev`.

1. Clone repository.

    ```sh
    git clone https://github.com/hillaryychan/ulauncher-fzf.git
    ```

1. (Optional) Install developer dependencies.  
    This is used to install dependencies for running `lint` and `format`.
    It will require Python 3.9 or higher and [uv](https://docs.astral.sh/uv/).

    ```sh
    make setup
    ```

1. Create a symlink to the Ulauncher extensions directory.

    ```sh
    make link
    ```

1. Stop Ulauncher.
1. Run Ulauncher and the extension.  
    If don't mind having other extensions running alongside this extension, you can start Ulauncher in developer and verbose mode.

    ```sh
    make start
    ```

    If you would like **only** this extension to run in Ulauncher.

    1. Run Ulauncher with no extensions and logging enabled.

        ```sh
        make dev
        ```

    1. In a separate terminal, run `ulauncher-fzf`.  
        The command to run the extension should be visible in the logging for Step 5i. It should look ***like*** this:

        ```sh
        VERBOSE=1 ULAUNCHER_WS_API=ws://127.0.0.1:5050/ulauncher-demo PYTHONPATH=/home/username/projects/ulauncher /usr/bin/python /home/username/.local/share/ulauncher/extensions/ulauncher-demo/main.py
        ```

Full list of targets for the command runners:

* `setup` - install developer dependencies
* `lint` - run code linters and formatter checks
* `format` - run code formatters
* `link` - create symlink to Ulauncher extensions directory
* `unlink` - remove symlink created by `link`
* `start` - run Ulauncher with logging enabled  
    **note:** this will also run **all** extensions present in `~/.local/share/ulauncher/extensions/`
* `dev` - run Ulauncher with no extensions and logging enabled

## Contributing

All contributions are welcome. Raise an issue or open a pull request.

## License

This source code is licensed under the [MIT license](LICENSE).
