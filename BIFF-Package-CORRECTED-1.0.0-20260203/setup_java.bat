@echo off
REM Setup Java environment for BIFF development
REM This sets JAVA_HOME and adds Java to PATH for the current session

echo Setting up Java environment for BIFF...
echo.

REM Set JAVA_HOME to Microsoft JDK 17 installation
set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.3.7-hotspot

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
