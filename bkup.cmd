
set cmd=git add "." --all
%cmd%
IF %ERRORLEVEL% NEQ 0 (
    pause
    exit
)
git commit -m "auto backup"
IF %ERRORLEVEL% NEQ 0 (
    pause
    exit
)
git pull origin master
IF %ERRORLEVEL% NEQ 0 (
    pause
    exit
)

git push origin master
IF %ERRORLEVEL% NEQ 0 (
    pause
    exit
)