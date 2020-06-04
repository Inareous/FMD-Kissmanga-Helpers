@echo off
:: Set your variable here
set "PYTHON_PATH="
set "SCRIPT_PATH="
set "FMD_PATH="
set "ADD_COOKIES="
set "URL="
set "IGNORE_CHKO=false"
set "USE_BROWSER=false"
::
set "modules_path=%FMD_PATH%\\config\\modules.json"
set "fmd_exe=%FMD_PATH%\\fmd.exe"
IF NOT "%ADD_COOKIES%" == "" ( set "ADD_COOKIES=--a "%ADD_COOKIES%"" )
IF NOT "%URL%" == "" ( set "URL=--url "%ADD_COOKIES%"" )
IF NOT "%IGNORE_CHKO%" == "true" (
    set "IGNORE_CHKO=--ignore-chko") ELSE (
    set "IGNORE_CHKO=")

IF "%USE_BROWSER%" == "true" (
    set "USE_BROWSER=--use-browser") ELSE (
    set "USE_BROWSER=")

START /wait "%PYTHON_PATH%" "%SCRIPT_PATH%" --path "%modules_path%" %ADD_COOKIES% %IGNORE_CHKO% %USE_BROWSER%
START "" %fmd_exe%

exit