@echo off
set "API_BASE=http://localhost:8000"

echo ==> GET /health
curl -s -o NUL -w "status: %%{http_code}\n" "%API_BASE%/health"

pause
