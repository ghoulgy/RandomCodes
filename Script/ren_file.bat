@echo off
setlocal enabledelayedexpansion
set counter=0

FOR /r %%i IN (*.json) DO (
  ::echo %%i
  set "name=!counter!.json" 
  ren "%%i" !name!
  set /a counter=counter+1
)
