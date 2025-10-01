@echo off
set "API_BASE=http://localhost:8000"
set "API_KEY=secret"

echo ==> GET /whoami con API key valida
curl -s -H "X-API-Key: %API_KEY%" "%API_BASE%/whoami"

pause
