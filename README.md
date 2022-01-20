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

## License

This source code is licensed under the [MIT license](LICENSE).
