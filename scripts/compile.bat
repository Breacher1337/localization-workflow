@echo off
setlocal enabledelayedexpansion

echo [INFO] Setting up Application JP Translation compilation...

REM Check if Application is running to prevent file lock issues
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-Process application -ErrorAction SilentlyContinue) { Write-Error 'Application is currently running. Please close the application before compiling to avoid file lock errors.'; exit 1 }"
if %ERRORLEVEL% neq 0 (
    exit /b %ERRORLEVEL%
)

REM Define paths
set APPLICATION_CORE=%APPLICATION_CORE_DIR%
set JAVASSIST_URL=https://repo1.maven.org/maven2/org/javassist/javassist/3.29.2-GA/javassist-3.29.2-GA.jar
set LIBS_DIR=libs
set JARS_DIR=jars
set SRC_DIR=source

REM Create directories if they don't exist
if not exist "%LIBS_DIR%" mkdir "%LIBS_DIR%"
if not exist "%JARS_DIR%" mkdir "%JARS_DIR%"
if not exist "build\classes" mkdir "build\classes"

REM Download Javassist if not present
if not exist "%LIBS_DIR%\javassist.jar" (
    echo [INFO] Downloading Javassist...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%JAVASSIST_URL%' -OutFile '%LIBS_DIR%\javassist.jar'"
)

REM Build Classpath
set CLASSPATH="%APPLICATION_CORE%\legacyapp.api.jar";"%APPLICATION_CORE%\log4j-1.2.9.jar";"%APPLICATION_CORE%\json.jar";"%APPLICATION_CORE%\lwjgl.jar";"%APPLICATION_CORE%\lwjgl_util.jar";"%LIBS_DIR%\javassist.jar"

REM Find all java source files
dir /s /B "%SRC_DIR%\*.java" > sources.txt

echo [INFO] Compiling Java sources...
javac -encoding UTF-8 --release 8 -d build\classes -cp %CLASSPATH% @sources.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Compilation failed.
    exit /b %ERRORLEVEL%
)


echo [INFO] Packaging jar file...
javac java_tools\src\MakeJar.java -d java_tools\src
java -cp java_tools\src MakeJar
del java_tools\src\MakeJar.class

echo [INFO] Copying dependencies to jars folder...
copy /Y "%LIBS_DIR%\javassist.jar" "%JARS_DIR%\" >nul

echo [INFO] Build successful!


