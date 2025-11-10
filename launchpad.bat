@echo off
setlocal

rem Get current directory name as project name
for %%I in (.) do set "PROJECT_NAME=%%~nxI"

setlocal enabledelayedexpansion

set BASE_FILES=-f docker-compose.base.yml
set LOCAL_FILES=%BASE_FILES% -f docker-compose.local.yml
set EXTERNAL_FILES=%BASE_FILES% -f docker-compose.external.yml
set COMPOSE_ARGS=-p %PROJECT_NAME%

rem Read local LLM backend from config file
set LOCAL_LLM_BACKEND=ollama
if exist local-llm.config (
    for /f "tokens=1,2 delims==" %%a in ('findstr /v "^#" local-llm.config ^| findstr "LOCAL_LLM_BACKEND"') do (
        set LOCAL_LLM_BACKEND=%%b
    )
)
rem Trim whitespace
for /f "tokens=* delims= " %%a in ("%LOCAL_LLM_BACKEND%") do set LOCAL_LLM_BACKEND=%%a

rem Read optional services from services.config
set SERVICE_FILES=
if exist services.config (
    for /f "tokens=1,2 delims==" %%a in ('findstr /v "^#" services.config') do (
        set SERVICE_NAME=%%a
        set SERVICE_ENABLED=%%b
        rem Trim whitespace
        for /f "tokens=* delims= " %%x in ("!SERVICE_ENABLED!") do set SERVICE_ENABLED=%%x
        
        rem Check if service is enabled (true)
        if /i "!SERVICE_ENABLED!"=="true" (
            rem Extract service name from ENABLE_SERVICENAME
            set SERVICE_NAME=%%a
            set SERVICE_NAME=!SERVICE_NAME:ENABLE_=!
            rem Convert to lowercase
            for %%y in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do call set SERVICE_NAME=%%SERVICE_NAME:%%y=%%y%%
            for %%y in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do call set SERVICE_NAME=%%SERVICE_NAME:%%y=%%y%%
            set SERVICE_NAME=!SERVICE_NAME:A=a!
            set SERVICE_NAME=!SERVICE_NAME:B=b!
            set SERVICE_NAME=!SERVICE_NAME:C=c!
            set SERVICE_NAME=!SERVICE_NAME:D=d!
            set SERVICE_NAME=!SERVICE_NAME:E=e!
            set SERVICE_NAME=!SERVICE_NAME:F=f!
            set SERVICE_NAME=!SERVICE_NAME:G=g!
            set SERVICE_NAME=!SERVICE_NAME:H=h!
            set SERVICE_NAME=!SERVICE_NAME:I=i!
            set SERVICE_NAME=!SERVICE_NAME:J=j!
            set SERVICE_NAME=!SERVICE_NAME:K=k!
            set SERVICE_NAME=!SERVICE_NAME:L=l!
            set SERVICE_NAME=!SERVICE_NAME:M=m!
            set SERVICE_NAME=!SERVICE_NAME:N=n!
            set SERVICE_NAME=!SERVICE_NAME:O=o!
            set SERVICE_NAME=!SERVICE_NAME:P=p!
            set SERVICE_NAME=!SERVICE_NAME:Q=q!
            set SERVICE_NAME=!SERVICE_NAME:R=r!
            set SERVICE_NAME=!SERVICE_NAME:S=s!
            set SERVICE_NAME=!SERVICE_NAME:T=t!
            set SERVICE_NAME=!SERVICE_NAME:U=u!
            set SERVICE_NAME=!SERVICE_NAME:V=v!
            set SERVICE_NAME=!SERVICE_NAME:W=w!
            set SERVICE_NAME=!SERVICE_NAME:X=x!
            set SERVICE_NAME=!SERVICE_NAME:Y=y!
            set SERVICE_NAME=!SERVICE_NAME:Z=z!
            
            rem Add service compose file
            set SERVICE_FILES=!SERVICE_FILES! -f docker-compose.!SERVICE_NAME!.yml
        )
    )
)

rem Append service files to compose file lists
set LOCAL_FILES=!LOCAL_FILES!!SERVICE_FILES!
set EXTERNAL_FILES=!EXTERNAL_FILES!!SERVICE_FILES!

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
echo Starting services with local LLM (%LOCAL_LLM_BACKEND%)...
echo.
echo.
echo ===========================================
echo ===========================================
echo.
echo     AI LAUNCHPAD STARTING
echo     Backend: %LOCAL_LLM_BACKEND%
echo.
echo     Once ready, open:
echo     http://localhost:8501
echo.
echo ===========================================
echo ===========================================
echo.
echo.
shift
set "COMPOSE_PROFILES=%LOCAL_LLM_BACKEND%"
docker compose %COMPOSE_ARGS% --profile %LOCAL_LLM_BACKEND% %LOCAL_FILES% up %1 %2 %3 %4 %5 %6 %7 %8 %9
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
echo Building services with local LLM (%LOCAL_LLM_BACKEND%)...
shift
set "COMPOSE_PROFILES=%LOCAL_LLM_BACKEND%"
docker compose %COMPOSE_ARGS% --profile %LOCAL_LLM_BACKEND% %LOCAL_FILES% build %1 %2 %3 %4 %5 %6 %7 %8 %9
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
echo   run-local      Start services with local LLM (backend: %LOCAL_LLM_BACKEND%)
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
echo Local LLM Backend:
echo   Current: %LOCAL_LLM_BACKEND%
echo   Configure: Edit local-llm.config (options: ollama, vllm)
echo.
echo Optional Services:
echo   Configure: Edit services.config to enable/disable services
echo   Example: ENABLE_POSTGRES=true
echo.
echo Examples:
echo   launchpad.bat run-local
echo   launchpad.bat run-local -d
echo   launchpad.bat stop
echo   launchpad.bat restart
echo   launchpad.bat logs llm-dispatcher
goto :eof