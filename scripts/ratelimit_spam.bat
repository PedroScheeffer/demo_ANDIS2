@echo off
set "API_BASE=http://localhost:8000"
set "API_KEY=secret"

echo ==> 12 requests rapidos a /health (espera varios 200 y luego 429)
for /L %%i in (1,1,12) do (
  curl -s -o NUL -w "status: %%{http_code}\n" -H "X-API-Key: %API_KEY%" "%API_BASE%/health"
)

pause
