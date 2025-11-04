@echo off
setlocal enabledelayedexpansion

REM Set your destination repo here
set TARGET=roxxie09/roxxiestrms

REM Create .github folder if it doesn't exist
if not exist .github mkdir .github

REM Start sync.yml
echo %TARGET%: > .github\sync.yml

REM Add all .html and .js files at root
for %%F in (*.html *.js) do (
    echo   - %%F>> .github\sync.yml
)

REM Add all top-level folders except .git and .github
for /d %%D in (*) do (
    if /I not "%%D"==".git" if /I not "%%D"==".github" (
        echo   - %%D/>> .github\sync.yml
    )
)

echo Done generating .github\sync.yml
endlocal
