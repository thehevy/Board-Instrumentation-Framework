# =============================================================================
# Start Marvin with automatic cleanup of existing instances
# =============================================================================
# Usage: .\start_marvin.ps1 -ConfigFile <config.xml> [-JavaArgs @("-vvvv", "-log", "output.html")]
# Example: .\start_marvin.ps1 -ConfigFile App.Config.xml -JavaArgs @("-vvvv")
#
# This script:
# 1. Checks if Marvin is already running with the same config
# 2. Stops the existing instance if found
# 3. Launches new instance with specified config
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ConfigFile,
    
    [Parameter(Mandatory=$false)]
    [string[]]$JavaArgs = @()
)

# Get absolute path to config file
$configPath = (Resolve-Path $ConfigFile -ErrorAction SilentlyContinue).Path
if (-not $configPath) {
    Write-Host "ERROR: Configuration file not found: $ConfigFile" -ForegroundColor Red
    exit 1
}

# Check for Java
try {
    java -version 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Java not found"
    }
} catch {
    Write-Host "ERROR: Java not found in PATH" -ForegroundColor Red
    Write-Host "Run setup_java.bat or setup_java.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Check for JAR file - support both development (build\libs\) and package (flat) structures
$devJarPath = "build\libs\BIFF.Marvin.jar"
$packageJarPath = "BIFF.Marvin.jar"

if (Test-Path $devJarPath) {
    $jarPath = $devJarPath
    $jarDir = "build\libs"
    $environment = "development"
} elseif (Test-Path $packageJarPath) {
    $jarPath = $packageJarPath
    $jarDir = "."
    $environment = "package"
} else {
    Write-Host "ERROR: BIFF.Marvin.jar not found" -ForegroundColor Red
    Write-Host "  Development: build\libs\BIFF.Marvin.jar" -ForegroundColor Yellow
    Write-Host "  Package:     BIFF.Marvin.jar" -ForegroundColor Yellow
    Write-Host "Run gradlew build first (if in development environment)" -ForegroundColor Yellow
    exit 1
}

Write-Host "Checking for existing Marvin instance with config: $configPath" -ForegroundColor Cyan

# Find and kill existing instance with same config
$existingProcesses = Get-WmiObject Win32_Process -Filter "name='java.exe'" | Where-Object {
    $_.CommandLine -like "*BIFF.Marvin.jar*" -and $_.CommandLine -like "*$configPath*"
}

if ($existingProcesses) {
    foreach ($proc in $existingProcesses) {
        Write-Host "Stopping existing Marvin instance (PID: $($proc.ProcessId))" -ForegroundColor Yellow
        Stop-Process -Id $proc.ProcessId -Force
    }
    Start-Sleep -Seconds 2
    Write-Host "Existing instance stopped" -ForegroundColor Green
} else {
    Write-Host "No existing instance found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Marvin with config: $configPath" -ForegroundColor Cyan
Write-Host "Additional args: $JavaArgs" -ForegroundColor Cyan
Write-Host ""

# Launch Marvin (navigate to JAR directory if needed)
if ($jarDir -ne ".") {
    Push-Location $jarDir
    try {
        $allArgs = @("-Xss1G", "-Xms1G", "-jar", "BIFF.Marvin.jar", "-i", $configPath) + $JavaArgs
        & java $allArgs
    } finally {
        Pop-Location
    }
} else {
    $allArgs = @("-Xss1G", "-Xms1G", "-jar", "BIFF.Marvin.jar", "-i", $configPath) + $JavaArgs
    & java $allArgs
}
