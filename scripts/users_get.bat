@echo off
set "API_BASE=http://localhost:8000"
set "API_KEY=secret"

echo ==> GET /api/users/
curl -s -L -H "X-API-Key: %API_KEY%" "%API_BASE%/api/users/"

pause
