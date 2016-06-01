@echo off
set add=git add "." --all
set commit=git commit -m "auto backup"
set pull=git pull origin master
set push=git push origin master

%add%
CALL :check_err

%commit%
CALL :check_err

%pull%
CALL :check_err

%push%
CALL :check_err

exit



:check_err
IF %ERRORLEVEL% NEQ 0 (
    pause
    exit
)
GOTO :eof