@echo off
REM Setup Java environment for BIFF development
REM This sets JAVA_HOME and adds Java to PATH for the current session

echo Setting up Java environment for BIFF...
echo.

REM Set JAVA_HOME. Prefer an already-valid JAVA_HOME, otherwise auto-detect the
REM newest Microsoft OpenJDK installed under "C:\Program Files\Microsoft".
if exist "%JAVA_HOME%\bin\java.exe" goto :have_java
set JAVA_HOME=
for /f "delims=" %%D in ('dir /b /ad /o-n "C:\Program Files\Microsoft\jdk-*" 2^>nul') do (
    if not defined JAVA_HOME if exist "C:\Program Files\Microsoft\%%D\bin\java.exe" set JAVA_HOME=C:\Program Files\Microsoft\%%D
)
if not defined JAVA_HOME set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.3.7-hotspot
:have_java

REM Add Java bin to PATH
set PATH=%JAVA_HOME%\bin;%PATH%

REM Verify Java is accessible
java -version
echo.

REM Check if JAVA_HOME is valid
if %ERRORLEVEL% EQU 0 (
    echo Java environment configured successfully!
    echo JAVA_HOME=%JAVA_HOME%
    echo.
    echo You can now run Gradle builds:
    echo   cd Marvin
    echo   gradlew buildDeps
    echo   gradlew build
) else (
    echo ERROR: Java not found at %JAVA_HOME%
    echo Please update JAVA_HOME path in this script
    exit /b 1
)
