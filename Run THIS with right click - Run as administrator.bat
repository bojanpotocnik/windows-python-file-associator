@echo off

:: Change working directory to the script directory
cd /D "%~dp0"

:: Run python script with Python 3"
py.exe associator.py

echo:
echo:This shall print out the desired Python version (>= Python 3.6):
print_version.py
