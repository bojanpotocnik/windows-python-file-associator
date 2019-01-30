Run the file `Run THIS with right click - Run as administrator.bat` with the administrator privileges.

On Windows, .py files are sometimes associated with Python 2.7 by default (installed out of the box).
This script is used to change the registry settings so that:

- double-clicking `.py` or `.pyc` file will run it using [Python Launcher for Windows](https://docs.python.org/3/using/windows.html#python-launcher-for-windows) (`py.exe`)

- drag-and-drop of single or multiple files to `.py` scripts will be enabled


Both features can be tested using [print_version.py](print_version.py) script, which can be run by double-clicking it or by dropping file(s) onto it. It shall output the Python version running it and all of the provided arguments (e.g. absolute paths to the dropped files).
