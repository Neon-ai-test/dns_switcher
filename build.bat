@echo off
echo Installing dependencies...
pip install pyinstaller pillow

echo.
echo Building application...
pyinstaller dns_switcher.spec

echo.
echo Build completed! Executable is located at dist/DNS_switcher.exe
echo.
pause