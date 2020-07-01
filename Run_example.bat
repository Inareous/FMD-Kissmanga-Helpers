@echo off
:: Set your variable here
set "PYTHON_PATH=C:\\Python38\python.exe"
:: Put 1 backslash on SCRIPT_PATH
set "SCRIPT_PATH=D:\\my_scripts\FMD-Kissmanga-Helpers\ks_cookies_to_fmd.py"
:: Put 2 backslash on FMD_PATH
set "FMD_PATH=D:\\my_programs\\fmd"
set "ADD_COOKIES=fullListMode=true;username=;password=;vns_readType1=0;"
set "URL="
set "USE_SELENIUM=true"
::
set "modules_path=%FMD_PATH%\\userdata\\modules.json"
set "fmd_exe=%FMD_PATH%\\fmd.exe"
IF NOT "%ADD_COOKIES%" == "" ( set "ADD_COOKIES=--a "%ADD_COOKIES%"" )
IF NOT "%URL%" == "" ( set "URL=--url "%URL%"" )

IF "%USE_SELENIUM%" == "true" (
    set "USE_SELENIUM=--use-selenium") ELSE (
    set "USE_SELENIUM=")

START /wait "%PYTHON_PATH%" "%SCRIPT_PATH%" --path "%modules_path%" %ADD_COOKIES% %IGNORE_CHKO% %USE_SELENIUM%
START "" "%fmd_exe%"

exit