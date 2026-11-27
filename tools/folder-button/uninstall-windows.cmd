@echo off
rem Undoes install-windows.cmd.
reg delete "HKCU\Software\Classes\roxie-raw" /f >nul 2>&1
echo Removed. The folder buttons won't open anything on this PC now.
pause
