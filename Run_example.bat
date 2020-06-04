@echo off
:: Set your variable here
set "PYTHON_PATH=C:\Python38\python.exe"
set "SCRIPT_PATH=D:\my_scripts\FMD-Kissmanga-Helpers\ks_cookies_to_fmd.py"
set "FMD_PATH=D:\\my_programs\\fmd"
set "ADD_COOKIES=fullListMode=true;username=;password=;vns_readType1=0;"
set "URL="
set "IGNORE_CHKO=false"
set "USE_BROWSER=true"
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