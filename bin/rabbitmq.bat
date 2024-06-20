@echo off

:: Determine the current directory of the batch file
set "SCRIPT_PATH=%~dp0"

REM Check for administrative privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges.
    echo Please right-click the batch file and select "Run as administrator."
    pause
    exit /b
)

REM Main script logic
if "%1" == "start" (
    goto :start_service
) else if "%1" == "stop" (
    goto :stop_service
) else if "%1" == "status" (
    goto :status
) else if "%1" == "help" (
    echo start - To start RabbitMQ service and app
    echo stop - To stop RabbitMQ service and app
    echo status - To show RabbitMQ status
    goto :end
) else (
    echo Invalid argument. Please use one of the following:
    echo start - To start RabbitMQ service and app
    echo stop - To stop RabbitMQ service and app
    echo status - To show RabbitMQ status
    goto :end
)

REM Function to start RabbitMQ service
:start_service
echo Checking RabbitMQ service status...
sc query RabbitMQ | find "RUNNING" >nul 2>&1
if %errorlevel% == 0 (
    echo RabbitMQ service is already running.
) else (
    echo Starting RabbitMQ service...
    net start RabbitMQ
    echo Verifying cookies...
    xcopy /y/r "C:\Windows\system32\config\systemprofile\.erlang.cookie" "C:\Users\%USERNAME%\.erlang.cookie"
    echo Cookies verified.
    cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.3\sbin"
    echo Starting RabbitMQ app...
    call rabbitmqctl start_app
    echo Startup successfull
)
goto :end

REM Function to stop RabbitMQ service
:stop_service
echo Checking RabbitMQ service status...
sc query RabbitMQ | find "RUNNING" >nul 2>&1
if %errorlevel% == 0 (
    echo Stopping RabbitMQ service...
    cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.3\sbin"
    call rabbitmqctl stop_app
    net stop RabbitMQ
    if %errorlevel% == 0 (
        echo RabbitMQ service stopped successfully.
    ) else (
        echo Failed to stop RabbitMQ service.
    )
) else (
    echo RabbitMQ service is not running.
)
goto :end

REM Function to show RabbitMQ status
:status
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.3\sbin"
echo Showing RabbitMQ status...
@REM call rabbitmqctl status
setlocal
set "output="
for /f "delims=" %%A in ('rabbitmqctl status 2^>^&1') do (
    if not defined output (
        set "output=%%A"
    )
)
if "%output:~0,5%" == "Error" (
    echo RabbitMQ service is not running. Use rabbitmq.bat start command to start the service.
) else if "%output:~0,6%" == "Status" (
    echo RabbitMQ service is up and runnning.
) else (
    echo Unknown error occured, contact administrator...
)
endlocal
goto :end

:end
cd %SCRIPT_PATH%