call settings

@echo off

setlocal

goto :header

:main
endlocal
setlocal EnableDelayedExpansion

set input=
set /p input=%user%@txman $ 

set parser=python %utils% --path %cd%

set i=0
for %%a in (%input%) do (
	set args[!i!]=%%a
	set /a i+=1
)

if "%args[0]%" EQU "help" goto help
if "%args[0]%" EQU "clear" goto header
if "%args[0]%" EQU "exit" goto end
if "%args[0]%" EQU "list" goto list
if "%args[0]%" EQU "log" goto log
if "%args[0]%" EQU "create" goto create
if "%args[0]%" EQU "remove" goto remove
goto invalid

:invalid
echo.
echo invalid command..
echo enter "help" to know more.
echo.
goto main

:help
echo.
echo.
echo anatomy of principal commands : [command] [flag]
echo.
echo.
echo # basic commands
echo.
echo  * help                Help menu.
echo  * clear               Clear screen.
echo  * exit                Leave txMan.
echo.
echo # main commands
echo.
echo  * list                Lists image files and prints on
echo                        the screen.
echo  * log                 Lists image files and saves in
echo                        a log file.
echo  * create              Creates *tx* files with the same
echo                        image name.
echo  * remove              Removes tx files.
echo.
echo # command flags
echo.
echo  * select              The command will be applied only
echo                        on selected images or directories.
echo                        A *selection* list will be required
echo                        and the components must be separated
echo                        by white spaces. Directories must
echo                        have "\" at the end.
echo  * here                The command will be applied on all
echo                        images in current directory.
echo  * tree                The command will be applied on all
echo                        images and dependencies in current
echo                        directory.
echo.
echo # command filters
echo.
echo  * all                 All images on group will be selected.
echo  * grey                Only float and grayscale images will
echo                        be selected, given a threshold.
echo  * color               Only colored or polychromatic images
echo                        will be selected, given a threshold.
echo  * regex               The selection will be given by an
echo                        regular expression.
echo.
goto main

:list
set parser=%parser% --list
if "%args[1]%" EQU "" (
	echo.
	echo list [flag]
	echo.
)
goto flag

:log
set parser=%parser% --log --list
if "%args[1]%" EQU "" (
	echo.
	echo log [flag]
	echo.
)
goto logfile

:create
set parser=%parser% --create --maketx %maketx%
if "%args[1]%" EQU "" (
	echo.
	echo create [flag]
	echo.
)
goto flag

:remove
set parser=%parser% --remove
if "%args[1]%" EQU "" (
	echo.
	echo remove [flag]
	echo.
)
goto flag

:logfile
set logname=
set /p logname="* filename > "
set parser=%parser% --logname %logname%
goto flag

:flag
if "%args[1]%" EQU "select" (
	set parser=%parser% --select --all
	goto selection
)
if "%args[1]%" EQU "here" (
	set parser=%parser% --here
	goto filter
)
if "%args[1]%" EQU "tree" (
	set parser=%parser% --tree
	goto filter
)
goto invalid

:selection
set names=
set /p names="* selection > "
set parser=%parser% --selection %names%
goto filter

:filter
set choice=
set /p choice="* filter > "
if "%choice%" EQU "" (
	echo.
	goto main
)
if "%choice%" EQU "all" (
	set parser=%parser% --all
	if "%args[0]%" EQU "create" (
		goto colorconvert
	) else goto execute
)
if "%choice%" EQU "grey" (
	set parser=%parser% --grey
	goto threshold
)
if "%choice%" EQU "color" (
	set parser=%parser% --color
	goto threshold
)
if "%choice%" EQU "regex" (
	set parser=%parser% --regex --all
	goto pattern
)
goto invalid

:threshold
set threshold=
set /p threshold="* threshold > "
set parser=%parser% --threshold "%threshold%"
if "%args[0]%" EQU "create" (
	goto colorconvert
) else goto execute

:pattern
set pattern=
set /p pattern="* pattern > "
set parser=%parser% --pattern %pattern%
if "%args[0]%" EQU "create" (
	goto colorconvert
) else goto execute

:colorconvert
set cconvert=
set /p cconvert="* color convert [Y|N]> "
if "%cconvert%" EQU "" (
	echo.
	goto main
)
if /i "%cconvert%" EQU "Y" (
	set parser=%parser% --colorconvert
	goto csfrom
)
if /i "%cconvert%" EQU "N" (
	goto execute
)
goto invalid

:csfrom
set csfrom=
set /p csfrom="* from > "
if /i "%csfrom%" EQU "linear" (
	set parser=%parser% --csfrom linear
	goto csto
)
if /i "%csfrom%" EQU "srgb" (
	set parser=%parser% --csfrom sRGB
	goto csto
)
if /i "%csfrom%" EQU "rec" (
	set parser=%parser% --csfrom Rec709
	goto csto
)
goto invalid

:csto
set csto=
set /p csto="* to > "
if /i "%csto%" EQU "linear" (
	set parser=%parser% --csto linear
	goto execute
)
if /i "%csto%" EQU "srgb" (
	set parser=%parser% --csto sRGB
	goto execute
)
if /i "%csto%" EQU "rec" (
	set parser=%parser% --csto Rec709
	goto execute
)
goto invalid

:execute
echo.
%parser%
echo.
goto main

:header
cls
echo ##########################################
echo.
echo ### Arnold's TX Manager command prompt ###
echo.
echo ###################### by Diego Inacio ###
echo.
echo ##########################################
echo.
goto main

:end
cls