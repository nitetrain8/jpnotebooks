git add "." --all
git commit -m "auto backup"
git pull origin master
IF %ERRORLEVEL% NEQ 0 (
    pause
    exit
)
git push origin master
pause