@echo off
set add=git add "." --all
set commit=git commit -m "auto backup"
set pull=git pull origin master
set push=git push origin master
@echo on
%add%
@echo off
CALL :check_err

@echo on
%commit%
@echo off
CALL :check_err

@echo on
%pull%
@echo off
CALL :check_err

@echo on
%push%
@echo off
CALL :check_err

exit



:check_err
IF %ERRORLEVEL% NEQ 0 (
    echo "Error: exiting"
    pause
    exit
)
GOTO :eof