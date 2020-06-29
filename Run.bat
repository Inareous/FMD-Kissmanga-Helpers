@echo off
:: Set your variable here
set "PYTHON_PATH="
set "SCRIPT_PATH="
set "FMD_PATH="
set "ADD_COOKIES="
set "URL="
set "IGNORE_CHKO=false"
set "USE_SELENIUM=true"
::
set "modules_path=%FMD_PATH%\\config\\modules.json"
set "fmd_exe=%FMD_PATH%\\fmd.exe"
IF NOT "%ADD_COOKIES%" == "" ( set "ADD_COOKIES=--a "%ADD_COOKIES%"" )
IF NOT "%URL%" == "" ( set "URL=--url "%URL%"" )

IF "%IGNORE_CHKO%" == "true" (
    set "IGNORE_CHKO=--ignore-chko") ELSE (
    set "IGNORE_CHKO=")

IF "%USE_SELENIUM%" == "true" (
    set "USE_SELENIUM=--use-selenium") ELSE (
    set "USE_SELENIUM=")

START /wait "%PYTHON_PATH%" "%SCRIPT_PATH%" --path "%modules_path%" %ADD_COOKIES% %IGNORE_CHKO% %USE_SELENIUM%
START "" "%fmd_exe%"

exit