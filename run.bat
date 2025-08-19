@echo off
echo Starting SwordFish with Docker...
echo.

echo Building and starting services...
docker-compose -f docker/docker-compose.yml up --build

echo.
echo Services stopped.
pause
