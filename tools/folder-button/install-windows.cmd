@echo off
rem Makes the folder buttons in the EPG logo dashboard open THIS copy's raw folder (for your Windows user only).
setlocal
set "HERE=%~dp0"
set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
set "CON=%SystemRoot%\System32\conhost.exe"
if not exist "%HERE%open-raw.ps1" (
  echo open-raw.ps1 is missing next to this file.
  pause
  exit /b 1
)
if not exist "%HERE%..\..\raw\" (
  echo Can't find the raw folder. Keep this folder at tools\folder-button inside the project.
  pause
  exit /b 1
)
reg add "HKCU\Software\Classes\roxie-raw" /ve /d "URL:Roxie raw folder" /f >nul || goto fail
reg add "HKCU\Software\Classes\roxie-raw" /v "URL Protocol" /d "" /f >nul || goto fail
reg add "HKCU\Software\Classes\roxie-raw\shell\open\command" /ve /d "\"%CON%\" \"%PS%\" -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%HERE%open-raw.ps1\" \"%%1\"" /f >nul || goto fail
echo Done. The folder buttons now open:
for %%I in ("%HERE%..\..\raw") do echo   %%~fI
echo.
echo The first time, your browser asks before opening it. Tick "Always allow" to skip that.
pause
exit /b 0
:fail
echo Couldn't save the setting.
pause
exit /b 1
