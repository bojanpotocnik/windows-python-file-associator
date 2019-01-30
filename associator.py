import enum
import platform
import subprocess
import sys
import winreg
from typing import Dict
from winreg import *

__author__ = "Bojan Potočnik"
__version__ = "1.0.0"


# noinspection SpellCheckingInspection
@enum.unique
class ValueType(enum.IntEnum):
    """See `Registry Value Types <https://docs.python.org/3/library/winreg.html#value-types>`_."""

    REG_BINARY = winreg.REG_BINARY
    """Binary data in any form."""
    REG_DWORD_LITTLE_ENDIAN = winreg.REG_DWORD_LITTLE_ENDIAN
    """A 32-bit number in little-endian format. Equivalent to REG_DWORD."""
    REG_DWORD_BIG_ENDIAN = winreg.REG_DWORD_BIG_ENDIAN
    """A 32-bit number in big-endian format."""
    REG_EXPAND_SZ = winreg.REG_EXPAND_SZ
    """Null-terminated string containing references to environment variables (%PATH%)."""
    REG_LINK = winreg.REG_LINK
    """A Unicode symbolic link."""
    REG_MULTI_SZ = winreg.REG_MULTI_SZ
    """A sequence of null-terminated strings, terminated by two null characters.
     Python handles this termination automatically."""
    REG_NONE = winreg.REG_NONE
    """No defined value type."""
    REG_QWORD_LITTLE_ENDIAN = winreg.REG_QWORD_LITTLE_ENDIAN
    """A 64-bit number in little-endian format. Equivalent to REG_QWORD."""
    REG_RESOURCE_LIST = winreg.REG_RESOURCE_LIST
    """A device-driver resource list."""
    REG_FULL_RESOURCE_DESCRIPTOR = winreg.REG_FULL_RESOURCE_DESCRIPTOR
    """A hardware setting."""
    REG_RESOURCE_REQUIREMENTS_LIST = winreg.REG_RESOURCE_REQUIREMENTS_LIST
    """A hardware resource list."""
    REG_SZ = winreg.REG_SZ
    """A null-terminated string."""


def print_key_info(key: HKEYType) -> None:
    num_sub_keys, num_values, last_modified = QueryInfoKey(key)
    print("QueryInfoKey", num_sub_keys, num_values, last_modified)

    try:
        key_value, key_type = QueryValueEx(key, None)
        key_type = ValueType(key_type)
        print("QueryValueEx", key_value, key_type)
    except FileNotFoundError:
        print("QueryValueEx", "(value not set)")


def register_shell_open_commands() -> None:
    """Associate programs which will open the specified file extensions."""
    # root = os.path.dirname(sys.executable)

    # > This is not required as Python Launcher is installed which will launch latest Python version.
    # > https://docs.python.org/3/using/windows.html#python-launcher-for-windows

    # However, on some machines Python 2.7 is set as a default Python executable.
    # https://docs.python.org/3.3/using/windows.html#executing-scripts-without-the-python-launcher

    associations: Dict[str, str] = {
        # "ArchiveFile",
        "CompiledFile": "py.exe",  # Compiled Python files (.pyc)
        # "Extension",
        "File": "py.exe",  # Python files (.py)
        # "NoConArchiveFile",
        # "NoConFile"  # No console Python files (.pyw)
    }

    for ft, executable in associations.items():
        key_path = rf"Python.{ft}\Shell\open\command"
        value = f'"{executable}" "%1" %*'

        with CreateKey(HKEY_CLASSES_ROOT, key_path) as key:  # type: HKEYType
            print(rf"Setting 'HKEY_CLASSES_ROOT\{key_path}' to '{value}'")
            SetValueEx(key, None, 0, ValueType.REG_SZ.value, value)


def associate_file_extensions_with_file_types() -> None:
    """Associate file extensions with file type classes."""
    # https://stackoverflow.com/a/34321695/5616255

    associations = {
        "py": "File",
        "pyc": "CompiledFile",
        "pyo": "CompiledFile",
        "pyw": "NoConFile",
        "pyz": "ArchiveFile",
        "pyzw": "NoConArchiveFile"
    }

    for extension, file_type in associations.items():
        # noinspection PyArgumentList
        p = subprocess.run(f"assoc .{extension}", shell=True, check=False, capture_output=True)
        old_association = p.stdout.decode().strip()

        # noinspection PyArgumentList
        p = subprocess.run(f"assoc .{extension}=Python.{file_type}", shell=True, check=False, capture_output=True)

        if p.returncode:
            if "Access is denied." in p.stderr.decode():
                raise PermissionError()
            else:
                raise RuntimeError()
        else:
            print(f".{extension} files associated with Python.{file_type}"
                  f" (previous association was '{old_association}')")


# noinspection SpellCheckingInspection
def register_drop_handlers() -> None:
    """
    Register a drop handler for a Python file type, it is called whenever
    an object is dragged over or dropped on a member of the file type.
    """
    # https://stackoverflow.com/a/142854/5616255
    # https://mindlesstechnology.wordpress.com/2008/03/29/make-python-scripts-droppable-in-windows/

    # DropHandler IDs
    # - Long File Names (WSH DropHandler):
    # drop_handler = ("{60254CA5-953B-11CF-8C96-00AA00B8708C}", "Long File Names (WSH DropHandler)")
    # - Short File Names (EXE DropHandler):
    # drop_handler = ("{86C86720-42A0-1069-A2E8-08002B30309D}", "Long File Names (WSH DropHandler)")
    # - The standard EXE DropHandler has problems with Unicode file paths, so Steve Dower created a shell
    #   extension library for Windows Python 3.5+, pyshellext.amd64.dll, that implements a new drop handler
    #   ( https://stackoverflow.com/questions/42818369/python-drag-and-drop-broken#comment72845379_42869472 ):
    #       {BEA218D2-6950-497B-9434-61683EC065FE}
    drop_handler = ("{BEA218D2-6950-497B-9434-61683EC065FE}", "pyshellext.amd64.dll (Steve Dower's DropHandler)")

    file_types = [
        "ArchiveFile",
        "CompiledFile",  # Compiled Python files (.pyc)
        # not this "Extension",
        "File",  # Python files (.py)
        "NoConArchiveFile",
        "NoConFile"  # No console Python files (.pyw)
    ]

    for ft in file_types:
        key_path = rf"Python.{ft}\shellex\DropHandler"
        with CreateKey(HKEY_CLASSES_ROOT, key_path) as key:  # type: HKEYType
            print(rf"Setting 'HKEY_CLASSES_ROOT\{key_path}' to '{drop_handler[1]}'")
            SetValueEx(key, None, 0, ValueType.REG_SZ.value, drop_handler[0])


def main() -> int:
    if platform.system() != "Windows":
        print("FAILURE: This script is Windows-only", file=sys.stderr)
        return -1

    try:
        register_shell_open_commands()
        associate_file_extensions_with_file_types()
        register_drop_handlers()
    except PermissionError:
        print("FAILURE: Run this script with administrator privileges.", file=sys.stderr)
        return -2


if __name__ == "__main__":
    exit(main())
