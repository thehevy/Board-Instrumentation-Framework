# setup-markdown-quality.ps1
# PowerShell version of markdown quality pre-commit hook installer

$ErrorActionPreference = "Stop"

$HOOK_PATH = ".git\hooks\pre-commit"

# Check if markdownlint-cli is installed
try {
    $null = Get-Command markdownlint -ErrorAction Stop
    Write-Host "✅ markdownlint-cli found" -ForegroundColor Green
} catch {
    Write-Host "⚠️  markdownlint-cli not found. Installing..." -ForegroundColor Yellow
    Write-Host "Please install Node.js first, then run: npm install -g markdownlint-cli"
    Write-Host "Download Node.js from: https://nodejs.org/"
    exit 1
}

# Create pre-commit hook
$hookContent = @'
#!/bin/bash
# Pre-commit hook: Validate markdown quality

# Get staged markdown files
STAGED_MD=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

if [ -z "$STAGED_MD" ]; then
    exit 0
fi

echo "🔍 Checking markdown quality..."

# Run validator on staged files
for file in $STAGED_MD; do
    python3 markdown_validator.py "$file"
    if [ $? -ne 0 ]; then
        echo "❌ Markdown quality issues found in $file"
        echo "💡 Run: python3 markdown_validator.py $file --fix"
        exit 1
    fi
done

echo "✅ All markdown files pass quality checks"
exit 0
'@

# Ensure hooks directory exists
$hooksDir = Split-Path $HOOK_PATH -Parent
if (!(Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
}

# Write hook file
Set-Content -Path $HOOK_PATH -Value $hookContent -Encoding UTF8

Write-Host "✅ Pre-commit hook installed at $HOOK_PATH" -ForegroundColor Green
Write-Host "📝 Markdown files will be validated before each commit" -ForegroundColor Cyan
Write-Host ""
Write-Host "To test: git commit (with staged .md files)"
Write-Host "To bypass: git commit --no-verify"
