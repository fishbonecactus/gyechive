@echo off

cd /d "%~dp0"

echo Gyechive 서버 시작...

start "" python -m http.server 8000

timeout /t 2 > nul

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --incognito --new-window http://localhost:8000

exit