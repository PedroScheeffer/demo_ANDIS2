@echo off
set "API_BASE=http://localhost:8000"

echo ==> GET /whoami con API key invalida
curl -s -o NUL -w "status: %%{http_code}\n" -H "X-API-Key: invalid" "%API_BASE%/whoami"

pause
