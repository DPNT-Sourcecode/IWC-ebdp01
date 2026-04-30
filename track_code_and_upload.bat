@if "%DEBUG%" == "" @echo off
setlocal

set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set SCRIPT_CURRENT_DIR=%DIRNAME%

set JAVA_BIN=%SCRIPT_CURRENT_DIR%\track\jdk\bin\java.exe
set JAR_FILE=%SCRIPT_CURRENT_DIR%\track\jar\track-code-and-upload.jar
set PARAM_CONFIG_FILE=%SCRIPT_CURRENT_DIR%\config\credentials.config
set PARAM_STORE_DIR=%SCRIPT_CURRENT_DIR%\track\localstore
set PARAM_SOURCECODE_DIR=%SCRIPT_CURRENT_DIR%\.

set CMD_LINE_ARGS=%*

echo Running on host, using bundled JDK

@echo on
"%JAVA_BIN%"                            ^
     -jar "%JAR_FILE%"                  ^
     "track-and-upload"                 ^
     --config "%PARAM_CONFIG_FILE%"     ^
     --store "%PARAM_STORE_DIR%"        ^
     --sourcecode "%PARAM_SOURCECODE_DIR%" ^
     %CMD_LINE_ARGS%
@echo off

endlocal
