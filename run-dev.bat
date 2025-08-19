@echo off
echo Starting SwordFish in development mode...
echo.

echo Building and starting services in background...
docker-compose -f docker/docker-compose.yml up --build -d

echo.
echo Services are running in background!
echo.
echo To view logs: docker-compose logs -f
echo To stop services: docker-compose down
echo To restart: docker-compose restart
echo.
echo API will be available at: http://localhost:8000
echo Database will be available at: localhost:5432
echo.
pause
