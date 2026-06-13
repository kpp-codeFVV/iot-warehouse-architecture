@echo off
setlocal

cd /d "%~dp0"

echo Stopping services...
docker compose -p iot-warehouse down
if errorlevel 1 (
  echo Failed to stop services.
  pause
  exit /b 1
)

echo Services stopped.
pause
