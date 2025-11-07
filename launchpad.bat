@echo off
setlocal

rem Get current directory name as project name
for %%I in (.) do set "PROJECT_NAME=%%~nxI"

set BASE_FILES=-f docker-compose.base.yml
set LOCAL_FILES=%BASE_FILES% -f docker-compose.local.yml
set EXTERNAL_FILES=%BASE_FILES% -f docker-compose.external.yml
set COMPOSE_ARGS=-p %PROJECT_NAME%

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="run-local" goto :run-local
if "%1"=="run-external" goto :run-external
if "%1"=="build-local" goto :build-local
if "%1"=="build-external" goto :build-external
if "%1"=="stop" goto :stop
if "%1"=="restart" goto :restart
if "%1"=="status" goto :status
if "%1"=="logs" goto :logs
if "%1"=="remove" goto :remove

echo Unknown command: %1
echo.
goto :help

:run-local
echo Starting services with local LLM...
echo.
echo.
echo ===========================================
echo ===========================================
echo.
echo     AI LAUNCHPAD STARTING
echo.
echo     Once ready, open:
echo     http://localhost:8501
echo.
echo ===========================================
echo ===========================================
echo.
echo.
shift
docker compose %COMPOSE_ARGS% %LOCAL_FILES% up %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :eof

:run-external
if not exist .env (
    echo Error: .env file not found!
    echo.
    echo To use an external LLM provider:
    echo 1. Copy a template: copy env-templates\openai .env
    echo 2. Edit .env and add your API key
    echo 3. Run this script again
    exit /b 1
)
echo Starting services with external LLM provider...
echo.
echo.
echo ===========================================
echo ===========================================
echo.
echo     AI LAUNCHPAD STARTING
echo.
echo     Once ready, open:
echo     http://localhost:8501
echo.
echo ===========================================
echo ===========================================
echo.
echo.
shift
docker compose %COMPOSE_ARGS% %EXTERNAL_FILES% up %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :eof

:build-local
echo Building services with local LLM...
shift
docker compose %COMPOSE_ARGS% %LOCAL_FILES% build %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :eof

:build-external
echo Building services for external LLM provider...
shift
docker compose %COMPOSE_ARGS% %EXTERNAL_FILES% build %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :eof

:stop
echo Stopping services...
shift
rem Just stop containers, don't remove them
docker compose %COMPOSE_ARGS% %LOCAL_FILES% stop %1 %2 %3 %4 %5 %6 %7 %8 %9 2>nul
if errorlevel 1 docker compose %COMPOSE_ARGS% %EXTERNAL_FILES% stop %1 %2 %3 %4 %5 %6 %7 %8 %9 2>nul
goto :eof

:restart
echo Restarting services...
shift
rem Restart whichever configuration is currently stopped
docker compose %COMPOSE_ARGS% %LOCAL_FILES% restart %1 %2 %3 %4 %5 %6 %7 %8 %9 2>nul
if errorlevel 1 docker compose %COMPOSE_ARGS% %EXTERNAL_FILES% restart %1 %2 %3 %4 %5 %6 %7 %8 %9 2>nul
goto :eof

:status
echo Project containers status:
docker compose %COMPOSE_ARGS% %LOCAL_FILES% ps 2>nul || docker compose %COMPOSE_ARGS% %EXTERNAL_FILES% ps 2>nul || echo No active compose configuration found
goto :eof

:logs
shift
docker compose %COMPOSE_ARGS% %LOCAL_FILES% logs -f %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :eof

:remove
echo WARNING: This will remove all containers and volumes for this project!
set /p CONFIRM="Are you sure? (y/N) "
if /i "%CONFIRM%"=="y" (
    echo Detecting project containers...
    
    rem Try graceful shutdown with compose
    echo Stopping services...
    docker compose %COMPOSE_ARGS% %LOCAL_FILES% down --remove-orphans 2>nul
    set "LLM_API_KEY=dummy"
    set "LLM_API_ENDPOINT=dummy"
    set "LLM_PROVIDER=dummy"
    docker compose %COMPOSE_ARGS% %EXTERNAL_FILES% down --remove-orphans 2>nul
    
    rem Remove only containers from this project by label
    echo Removing project containers...
    for /f "tokens=*" %%i in ('docker ps -a -q --filter "label=com.docker.compose.project.working_dir=%CD:\=/%"') do (
        if not "%%i"=="" docker rm -f %%i 2>nul
    )
    
    rem Remove volumes by project name pattern
    echo Removing project volumes...
    docker volume ls -q | findstr /i "%PROJECT_NAME%" >nul 2>&1
    if not errorlevel 1 (
        for /f "tokens=*" %%i in ('docker volume ls -q ^| findstr /i "%PROJECT_NAME%"') do docker volume rm -f %%i 2>nul
    )
    
    echo Project containers and volumes removed
) else (
    echo Cancelled
)
goto :eof

:help
echo Usage: launchpad.bat [command]
echo.
echo Commands:
echo   run-local      Start services with local LLM
echo   run-external   Start services with external LLM provider
echo   build-local    Build containers for local LLM
echo   build-external Build containers for external LLM
echo   stop           Stop services (containers remain)
echo   restart        Restart stopped services
echo   status         Show status of project containers
echo   logs           Show logs from running services
echo   remove         Remove all project containers and volumes
echo   help           Show this help message
echo.
echo Examples:
echo   launchpad.bat run-local
echo   launchpad.bat run-local -d
echo   launchpad.bat stop
echo   launchpad.bat restart
echo   launchpad.bat logs llm-dispatcher
goto :eof