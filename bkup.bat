@echo off
set add=git add "." --all
set diff=git diff-index --quiet HEAD
set commit=git commit -m "auto backup"
set pull=git pull origin master
set push=git push origin master
@echo on
%add%
@echo off
CALL :check_err
 
@echo on
%diff% || %commit%
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
pause

:check_err
IF %ERRORLEVEL% NEQ 0 (
    echo "Error: exiting"
    pause
    exit
)
GOTO :eof