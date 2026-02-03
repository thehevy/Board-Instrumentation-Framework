# Setup Java environment for BIFF development (PowerShell)
# This sets JAVA_HOME and adds Java to PATH for the current session

Write-Host "Setting up Java environment for BIFF..." -ForegroundColor Cyan
Write-Host ""

# Set JAVA_HOME to Microsoft JDK 17 installation
$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-17.0.3.7-hotspot"

# Add Java bin to PATH
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

# Verify Java is accessible
try {
    java -version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Java environment configured successfully!" -ForegroundColor Green
        Write-Host "JAVA_HOME=$env:JAVA_HOME" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now run Gradle builds:" -ForegroundColor Yellow
        Write-Host "  cd Marvin" -ForegroundColor White
        Write-Host "  .\gradlew buildDeps" -ForegroundColor White
        Write-Host "  .\gradlew build" -ForegroundColor White
        Write-Host ""
        Write-Host "Or use the quickstart:" -ForegroundColor Yellow
        Write-Host "  cd biff-agents" -ForegroundColor White
        Write-Host "  python -m biff_cli quickstart" -ForegroundColor White
    } else {
        throw "Java command failed"
    }
} catch {
    Write-Host "ERROR: Java not found at $env:JAVA_HOME" -ForegroundColor Red
    Write-Host "Please update JAVA_HOME path in this script" -ForegroundColor Red
    exit 1
}
