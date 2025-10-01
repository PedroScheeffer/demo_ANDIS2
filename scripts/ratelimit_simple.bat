@echo off
set "API_BASE=http://localhost:8000"
set "API_KEY=secret"

echo ==> 1er request a /health
curl -s -o NUL -w "status: %%{http_code}\n" -H "X-API-Key: %API_KEY%" "%API_BASE%/health"

echo ==> 2do request inmediato a /health (esperado 200 o 429 si se supero limite)
curl -s -o NUL -w "status: %%{http_code}\n" -H "X-API-Key: %API_KEY%" "%API_BASE%/health"

pause
